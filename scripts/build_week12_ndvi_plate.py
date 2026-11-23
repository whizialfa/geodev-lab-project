"""Week 12 AMAC NDVI plate. Run with QGIS's Python.

    env -u PYTHONPATH /Applications/QGIS.app/Contents/MacOS/bin/python3.9 \\
        scripts/build_week12_ndvi_plate.py
"""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("QGIS_PREFIX_PATH", "/Applications/QGIS.app/Contents/MacOS")
os.environ.setdefault("PROJ_LIB", "/Applications/QGIS.app/Contents/Resources/proj")
os.environ.setdefault("GDAL_DATA", "/Applications/QGIS.app/Contents/Resources/gdal")

from qgis.core import (  # noqa: E402
    Qgis,
    QgsApplication,
    QgsColorRampShader,
    QgsCoordinateReferenceSystem,
    QgsFillSymbol,
    QgsGeometry,
    QgsLayoutExporter,
    QgsLayoutItem,
    QgsLayoutItemLabel,
    QgsLayoutItemMap,
    QgsLayoutItemPicture,
    QgsLayoutItemScaleBar,
    QgsLayoutItemShape,
    QgsLayoutMeasurement,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsPalLayerSettings,
    QgsPointXY,
    QgsPrintLayout,
    QgsProject,
    QgsProperty,
    QgsRasterLayer,
    QgsRasterShader,
    QgsRectangle,
    QgsScaleBarSettings,
    QgsSingleBandPseudoColorRenderer,
    QgsSingleSymbolRenderer,
    QgsTextBackgroundSettings,
    QgsTextBufferSettings,
    QgsTextFormat,
    QgsUnitTypes,
    QgsVectorLayer,
    QgsVectorLayerSimpleLabeling,
)
from qgis.PyQt.QtCore import QSizeF, Qt  # noqa: E402
from qgis.PyQt.QtGui import QColor, QFont  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
NDVI = ROOT / "data" / "raw" / "week12_amac" / "ndvi_amac.tif"
WARDS_GPKG = ROOT / "data" / "processed" / "amac_analysis_ready.gpkg"
NORTH_SVG = ROOT / "qgis" / "styles" / "north_arrow_white.svg"
OUT_PNG = ROOT / "month-03" / "week-12" / "my_map.png"
QGZ = ROOT / "qgis" / "week12_amac_ndvi.qgz"

CRS = "EPSG:32632"
MM = QgsUnitTypes.LayoutMillimeters
FRAME_X = FRAME_Y = 8.0
FRAME_W = 404.0
FRAME_H = 281.0
TITLE_W = 128.0
TITLE_H = 32.0
NOTE_W = 210.0
NOTE_H = 38.0
NOTE_BOTTOM = 8.0
GAP = 3.0
BOTTOM_CLEAR = 6.0
CREDIT = "©Wisdom Akpabio  ·  Basemap © Esri"

TITLE = "GREENNESS IN AMAC"
SUBTITLE = "NDVI from Landsat-9, 8 Nov 2024"
LEGEND_TITLE = "NDVI"
CAPTION = (
    "Colour shows how green each 30 m Landsat cell is inside the ten study wards "
    "(NDVI from red and near-infrared reflectance). "
    "The raster is clipped to the ward outlines — nothing outside the study is drawn. "
    "Higher values mean denser vegetation; yellow and red mark built-up ground, bare soil or water."
)
PINNED = ("Kabusa", "Gwarinpa", "Garki", "Wuse", "Karu", "Nyanya", "City Centre", "Dutse", "Kubwa", "Usuma")


def _place(layout, item, x, y, w=None, h=None) -> None:
    layout.addLayoutItem(item)
    item.attemptMove(QgsLayoutPoint(x, y, MM))
    if w is not None and h is not None:
        item.attemptResize(QgsLayoutSize(w, h, MM))


def _white_box(layout, x, y, w, h) -> QgsLayoutItemShape:
    box = QgsLayoutItemShape(layout)
    box.setShapeType(QgsLayoutItemShape.Rectangle)
    box.setSymbol(
        QgsFillSymbol.createSimple(
            {
                "color": "255,255,255,255",
                "outline_color": "0,0,0,255",
                "outline_width": "0.45",
                "outline_width_unit": "MM",
            }
        )
    )
    box.setFrameEnabled(False)
    box.setZValue(20)
    _place(layout, box, x, y, w, h)
    return box


def _item_box(item):
    tl = item.positionAtReferencePoint(QgsLayoutItem.UpperLeft)
    size = item.sizeWithUnits()
    return (float(tl.x()) - FRAME_X, float(tl.y()) - FRAME_Y, float(size.width()), float(size.height()))


def _grow(box, pad):
    x, y, w, h = box
    return (x - pad, y - pad, w + 2 * pad, h + 2 * pad)


def _norm_geom(geom: QgsGeometry, city: QgsRectangle) -> QgsGeometry:
    xmin, ymax = city.xMinimum(), city.yMaximum()
    cw, ch = city.width(), city.height()

    def ring(r):
        return [QgsPointXY((p.x() - xmin) / cw, (ymax - p.y()) / ch) for p in r]

    g = QgsGeometry(geom).simplify(max(cw, ch) / 200.0)
    if g.isMultipart():
        return QgsGeometry.fromMultiPolygonXY([[ring(r) for r in poly] for poly in g.asMultiPolygon()])
    return QgsGeometry.fromPolygonXY([ring(r) for r in g.asPolygon()])


def _framed_extent(city: QgsRectangle, city_poly: QgsGeometry, boxes) -> QgsRectangle:
    cw, ch = city.width(), city.height()
    padded = [(x - GAP, y - GAP, w + 2 * GAP, h + 2 * GAP) for x, y, w, h in boxes]
    norm = _norm_geom(city_poly, city)

    def hits(cx, cy, wmm, hmm):
        for x, y, w, h in padded:
            fg = QgsGeometry.fromRect(
                QgsRectangle((x - cx) / wmm, (y - cy) / hmm, (x + w - cx) / wmm, (y + h - cy) / hmm)
            )
            if norm.intersects(fg):
                return True
        return False

    def place(wmm, nx=15, ny=13):
        hmm = wmm * ch / cw
        x1 = FRAME_W - 3.0 - wmm
        y1 = FRAME_H - 3.0 - hmm
        if x1 < 3.0 or y1 < 3.0:
            return None
        tx = 0.5 * (FRAME_W - wmm)
        ty = 0.5 * (FRAME_H - hmm)
        best, best_d = None, 1e18
        for i in range(nx):
            cx = 3.0 + (x1 - 3.0) * i / (nx - 1)
            for j in range(ny):
                cy = 3.0 + (y1 - 3.0) * j / (ny - 1)
                if hits(cx, cy, wmm, hmm):
                    continue
                d = (cx - tx) ** 2 + (cy - ty) ** 2
                if d < best_d:
                    best, best_d = (cx, cy, wmm, hmm), d
        return best

    lo, hi = 40.0, min(FRAME_W - 6.0, (FRAME_H - 6.0) * cw / ch)
    best = place(lo)
    for _ in range(28):
        mid = 0.5 * (lo + hi)
        got = place(mid)
        if got is None:
            hi = mid
        else:
            best, lo = got, mid
    if best is None:
        raise RuntimeError("could not place study area on the page")
    best = place(best[2], nx=40, ny=30) or best
    cx, cy, wmm, hmm = best
    print(f"  study area {wmm:.0f}×{hmm:.0f} mm at ({cx:.0f},{cy:.0f})")
    view_w = FRAME_W * cw / wmm
    view_h = FRAME_H * ch / hmm
    xmin = city.xMinimum() - cx / FRAME_W * view_w
    ymax = city.yMaximum() + cy / FRAME_H * view_h
    return QgsRectangle(xmin, ymax - view_h, xmin + view_w, ymax)


def _ward_labels(layer: QgsVectorLayer) -> None:
    settings = QgsPalLayerSettings()
    settings.fieldName = "ward"
    settings.placement = Qgis.LabelPlacement.OverPoint
    settings.centroidInside = True
    settings.displayAll = True
    settings.obstacle = False
    settings.setUnplacedVisibility(Qgis.UnplacedLabelVisibility.NeverShow)
    settings.placementSettings().setOverlapHandling(Qgis.LabelOverlapHandling.AllowOverlapAtNoCost)
    fmt = QgsTextFormat()
    font = QFont("Helvetica", 12, QFont.Bold)
    fmt.setFont(font)
    fmt.setSize(12)
    fmt.setSizeUnit(QgsUnitTypes.RenderPoints)
    fmt.setColor(QColor(20, 20, 20))
    buf = QgsTextBufferSettings()
    buf.setEnabled(True)
    buf.setSize(2.0)
    buf.setSizeUnit(QgsUnitTypes.RenderPoints)
    buf.setColor(QColor(255, 255, 255))
    fmt.setBuffer(buf)
    bg = QgsTextBackgroundSettings()
    bg.setEnabled(False)
    fmt.setBackground(bg)
    settings.setFormat(fmt)
    pins = ",".join(f"'{n}'" for n in PINNED)
    settings.dataDefinedProperties().setProperty(
        QgsPalLayerSettings.Priority,
        QgsProperty.fromExpression(
            f'CASE WHEN "ward" IN ({pins}) THEN 10 ELSE scale_linear($area, 0, maximum($area), 3, 8) END'
        ),
    )
    layer.setLabeling(QgsVectorLayerSimpleLabeling(settings))
    layer.setLabelsEnabled(True)


def _style_ndvi(layer: QgsRasterLayer) -> None:
    shader = QgsRasterShader()
    ramp = QgsColorRampShader()
    # Discrete classes → short range-only legend rows (house style).
    ramp.setColorRampType(QgsColorRampShader.Discrete)
    items = [
        QgsColorRampShader.ColorRampItem(0.0, QColor(215, 48, 39), "≤ 0"),
        QgsColorRampShader.ColorRampItem(0.2, QColor(254, 224, 139), "0–0.2"),
        QgsColorRampShader.ColorRampItem(0.4, QColor(166, 217, 106), "0.2–0.4"),
        QgsColorRampShader.ColorRampItem(0.6, QColor(26, 152, 80), "0.4–0.6"),
        QgsColorRampShader.ColorRampItem(1.0, QColor(0, 104, 55), "> 0.6"),
    ]
    ramp.setColorRampItemList(items)
    shader.setRasterShaderFunction(ramp)
    renderer = QgsSingleBandPseudoColorRenderer(layer.dataProvider(), 1, shader)
    renderer.setClassificationMin(-0.2)
    renderer.setClassificationMax(0.8)
    layer.setRenderer(renderer)
    layer.setOpacity(0.88)


NDVI_CLASSES = [
    (QColor(215, 48, 39), "≤ 0"),
    (QColor(254, 224, 139), "0–0.2"),
    (QColor(166, 217, 106), "0.2–0.4"),
    (QColor(26, 152, 80), "0.4–0.6"),
    (QColor(0, 104, 55), "> 0.6"),
]


def _legend(layout) -> QgsLayoutItemShape:
    """Hand-built legend: title + range rows only (no Band 1 / Gray noise)."""
    inset = 2.5
    sw, sh = 5.0, 3.8
    row_gap = 1.0
    title_h = 6.0
    label_gap = 1.6
    rows = len(NDVI_CLASSES)
    inner_h = title_h + rows * sh + (rows - 1) * row_gap
    # widest label "~0.2–0.4" ≈ 18 mm at 12 pt
    box_w = inset + sw + label_gap + 18.0 + inset
    box_h = inset + inner_h + inset
    box_x, box_y = 14.0, 283.0 - box_h
    panel = _white_box(layout, box_x, box_y, box_w, box_h)

    title = QgsLayoutItemLabel(layout)
    title.setText(LEGEND_TITLE)
    title.setFont(QFont("Arial", 13, QFont.Bold))
    title.setFontColor(QColor(0, 0, 0))
    title.setHAlign(Qt.AlignLeft)
    title.setVAlign(Qt.AlignVCenter)
    title.setZValue(21)
    _place(layout, title, box_x + inset, box_y + inset, box_w - 2 * inset, title_h)

    y0 = box_y + inset + title_h
    for i, (color, label) in enumerate(NDVI_CLASSES):
        y = y0 + i * (sh + row_gap)
        swatch = QgsLayoutItemShape(layout)
        swatch.setShapeType(QgsLayoutItemShape.Rectangle)
        swatch.setSymbol(
            QgsFillSymbol.createSimple(
                {
                    "color": f"{color.red()},{color.green()},{color.blue()},255",
                    "outline_color": "0,0,0,180",
                    "outline_width": "0.2",
                    "outline_width_unit": "MM",
                }
            )
        )
        swatch.setFrameEnabled(False)
        swatch.setZValue(21)
        _place(layout, swatch, box_x + inset, y, sw, sh)

        lab = QgsLayoutItemLabel(layout)
        lab.setText(label)
        lab.setFont(QFont("Arial", 12))
        lab.setFontColor(QColor(0, 0, 0))
        lab.setHAlign(Qt.AlignLeft)
        lab.setVAlign(Qt.AlignVCenter)
        lab.setZValue(21)
        _place(layout, lab, box_x + inset + sw + label_gap, y, 18.0, sh)

    print(f"  legend {box_w:.1f}×{box_h:.1f} mm at ({box_x:.0f},{box_y:.0f})")
    return panel


def main() -> Path:
    if not NDVI.exists():
        raise SystemExit(f"Missing {NDVI}. Run month-03/week-12/my_index.py first.")

    QgsApplication.setPrefixPath(os.environ["QGIS_PREFIX_PATH"], True)
    app = QgsApplication([], False)
    app.initQgis()

    project = QgsProject.instance()
    project.clear()
    project.setCrs(QgsCoordinateReferenceSystem(CRS))

    basemap = QgsRasterLayer(
        "type=xyz&url=https://server.arcgisonline.com/ArcGIS/rest/services/"
        "Canvas/World_Light_Gray_Base/MapServer/tile/%7Bz%7D/%7By%7D/%7Bx%7D"
        "&zmax=16&zmin=0&crs=EPSG3857",
        "Esri light grey",
        "wms",
    )
    ndvi = QgsRasterLayer(str(NDVI), "NDVI", "gdal")
    wards = QgsVectorLayer(f"{WARDS_GPKG}|layername=amac_wards", "Ward", "ogr")
    for lyr in (basemap, ndvi, wards):
        if not lyr.isValid():
            raise RuntimeError(f"layer failed to load: {lyr.name()}")

    _style_ndvi(ndvi)
    wards.setRenderer(
        QgsSingleSymbolRenderer(
            QgsFillSymbol.createSimple(
                {
                    "color": "0,0,0,0",
                    "outline_color": "70,70,70,220",
                    "outline_width": "0.28",
                    "outline_width_unit": "MM",
                }
            )
        )
    )
    _ward_labels(wards)

    from qgis.core import QgsFeature

    outline = QgsVectorLayer(f"Polygon?crs={CRS}", "Study boundary", "memory")
    outline_data = outline.dataProvider()
    union = QgsGeometry()
    first = True
    for feat in wards.getFeatures():
        g = feat.geometry()
        if first:
            union = QgsGeometry(g)
            first = False
        else:
            union = union.combine(g)
    out_feat = QgsFeature()
    out_feat.setGeometry(union)
    outline_data.addFeature(out_feat)
    outline.updateExtents()
    outline.setRenderer(
        QgsSingleSymbolRenderer(
            QgsFillSymbol.createSimple(
                {
                    "color": "0,0,0,0",
                    "outline_color": "0,0,0,255",
                    "outline_width": "0.8",
                    "outline_width_unit": "MM",
                }
            )
        )
    )

    for lyr in (basemap, ndvi, wards, outline):
        project.addMapLayer(lyr)

    layout = QgsPrintLayout(project)
    layout.initializeDefaults()
    layout.setName("AMAC NDVI")
    for item in list(layout.items()):
        if isinstance(item, QgsLayoutItemMap):
            layout.removeLayoutItem(item)
    layout.pageCollection().page(0).setPageSize(QgsLayoutSize(420, 297, MM))

    map_item = QgsLayoutItemMap(layout)
    map_item.setFrameEnabled(True)
    map_item.setFrameStrokeColor(QColor(0, 0, 0))
    map_item.setFrameStrokeWidth(QgsLayoutMeasurement(0.55, MM))
    map_item.setCrs(QgsCoordinateReferenceSystem(CRS))
    map_item.setKeepLayerSet(True)
    map_item.setKeepLayerStyles(True)
    map_item.setLayers([outline, wards, ndvi, basemap])
    map_item.setZValue(0)
    _place(layout, map_item, FRAME_X, FRAME_Y, FRAME_W, FRAME_H)
    map_item.setFixedSize(QgsLayoutSize(FRAME_W, FRAME_H, MM))

    city_poly = QgsGeometry(union)
    city = city_poly.boundingBox()
    map_item.setExtent(city)

    title_panel = _white_box(layout, FRAME_X, FRAME_Y, TITLE_W, TITLE_H)
    title = QgsLayoutItemLabel(layout)
    title.setText(f"{TITLE}\n{SUBTITLE}")
    title.setFont(QFont("Arial", 15, QFont.Bold))
    title.setFontColor(QColor(0, 0, 0))
    title.setHAlign(Qt.AlignHCenter)
    title.setVAlign(Qt.AlignVCenter)
    title.setMargin(2.0)
    title.setZValue(21)
    _place(layout, title, FRAME_X, FRAME_Y, TITLE_W, TITLE_H)

    north = QgsLayoutItemPicture(layout)
    north.setMode(QgsLayoutItemPicture.FormatSVG)
    north.setPicturePath(str(NORTH_SVG))
    north.setLinkedMap(map_item)
    north.setNorthMode(QgsLayoutItemPicture.GridNorth)
    north.setFrameEnabled(False)
    north.setBackgroundEnabled(False)
    north.setZValue(20)
    _place(layout, north, 372, 10, 34, 42)

    legend = _legend(layout)
    leg_w = legend.sizeWithUnits().width()

    scale = QgsLayoutItemScaleBar(layout)
    scale.setLinkedMap(map_item)
    scale.setStyle("Line Ticks Up")
    scale.setUnits(QgsUnitTypes.DistanceKilometers)
    scale.setSegmentSizeMode(QgsScaleBarSettings.SegmentSizeFitWidth)
    scale.setMinimumBarWidth(62)
    scale.setMaximumBarWidth(82)
    scale.setNumberOfSegments(2)
    scale.setNumberOfSegmentsLeft(0)
    scale.setUnitLabel("km")
    scale.setFont(QFont("Arial", 11))
    scale.setFontColor(QColor(0, 0, 0))
    scale.setHeight(2.4)
    scale.setLineWidth(0.5)
    scale.setLineColor(QColor(0, 0, 0))
    scale.setBoxContentSpace(1.4)
    scale.setFrameEnabled(False)
    scale.setBackgroundEnabled(False)
    scale.setZValue(20)
    layout.addLayoutItem(scale)
    scale.refresh()
    scale.setReferencePoint(QgsLayoutItem.LowerRight)
    scale.attemptMove(QgsLayoutPoint(400, 283, MM))
    scale.refresh()
    scale_w = scale.sizeWithUnits().width()

    gap_left = 14.0 + leg_w + GAP
    gap_right = 400.0 - scale_w - GAP
    avail = max(gap_right - gap_left, 80.0)
    note_w = min(NOTE_W, avail)
    note_x = gap_left + 0.5 * (avail - note_w)
    note_y = FRAME_Y + FRAME_H - NOTE_BOTTOM - NOTE_H
    note_panel = _white_box(layout, note_x, note_y, note_w, NOTE_H)
    note = QgsLayoutItemLabel(layout)
    note.setText(CAPTION)
    note.setFont(QFont("Arial", 12, QFont.Bold))
    note.setFontColor(QColor(0, 0, 0))
    note.setHAlign(Qt.AlignHCenter)
    note.setVAlign(Qt.AlignVCenter)
    note.setMargin(3.0)
    note.setZValue(21)
    _place(layout, note, note_x, note_y, note_w, NOTE_H)

    credit = QgsLayoutItemLabel(layout)
    credit.setText(CREDIT)
    fmt = QgsTextFormat()
    fmt.setFont(QFont("Arial", 7))
    fmt.setSize(7)
    fmt.setSizeUnit(QgsUnitTypes.RenderPoints)
    fmt.setColor(QColor(0, 0, 0))
    buf = QgsTextBufferSettings()
    buf.setEnabled(True)
    buf.setSize(0.6)
    buf.setSizeUnit(QgsUnitTypes.RenderMillimeters)
    buf.setColor(QColor(255, 255, 255))
    fmt.setBuffer(buf)
    credit.setTextFormat(fmt)
    credit.setHAlign(Qt.AlignRight)
    credit.setVAlign(Qt.AlignBottom)
    credit.setMargin(0)
    credit.setZValue(22)
    _place(layout, credit, 400.0 - scale_w, 283.0 - scale.sizeWithUnits().height() - 9.0, scale_w, 8.0)

    boxes = [
        _item_box(title_panel),
        _item_box(north),
        _grow(_item_box(legend), BOTTOM_CLEAR),
        _grow(_item_box(note_panel), BOTTOM_CLEAR),
        _grow(_item_box(scale), BOTTOM_CLEAR),
        _grow(_item_box(credit), BOTTOM_CLEAR),
    ]
    map_item.setExtent(_framed_extent(city, city_poly, boxes))
    map_item.refresh()
    scale.refresh()
    project.layoutManager().addLayout(layout)

    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    for path in (OUT_PNG, OUT_PNG.with_suffix(".pdf")):
        if path.exists():
            path.unlink()
    exporter = QgsLayoutExporter(layout)
    img = QgsLayoutExporter.ImageExportSettings()
    img.dpi = 200
    img.generateWorldFile = False
    img.exportMetadata = False
    if exporter.exportToImage(str(OUT_PNG), img) != QgsLayoutExporter.Success:
        raise RuntimeError("PNG export failed")
    exporter.exportToPdf(str(OUT_PNG.with_suffix(".pdf")), QgsLayoutExporter.PdfExportSettings())

    project.write(str(QGZ))
    app.exitQgis()
    print("wrote", OUT_PNG)
    return OUT_PNG


if __name__ == "__main__":
    main()
