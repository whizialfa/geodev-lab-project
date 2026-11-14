"""Week 11 AMAC 2 km facility-reach plate. Run with QGIS's Python.

    env -u PYTHONPATH /Applications/QGIS.app/Contents/MacOS/bin/python3.9 \\
        scripts/build_week11_reach_plate.py
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
    QgsCoordinateReferenceSystem,
    QgsFillSymbol,
    QgsGeometry,
    QgsLayoutExporter,
    QgsLayoutItem,
    QgsLayoutItemLabel,
    QgsLayoutItemLegend,
    QgsLayoutItemMap,
    QgsLayoutItemPicture,
    QgsLayoutItemScaleBar,
    QgsLayoutItemShape,
    QgsLayoutMeasurement,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsLegendRenderer,
    QgsLegendStyle,
    QgsMarkerSymbol,
    QgsPalLayerSettings,
    QgsPointXY,
    QgsPrintLayout,
    QgsProject,
    QgsProperty,
    QgsRasterLayer,
    QgsRectangle,
    QgsScaleBarSettings,
    QgsSingleSymbolRenderer,
    QgsTextBufferSettings,
    QgsTextFormat,
    QgsUnitTypes,
    QgsVectorLayer,
    QgsVectorLayerSimpleLabeling,
)
from qgis.PyQt.QtCore import Qt  # noqa: E402
from qgis.PyQt.QtGui import QColor, QFont  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
REACH = ROOT / "data" / "processed" / "week11_amac_reach.gpkg"
FAC = ROOT / "data" / "processed" / "amac_health_facilities.gpkg"
NORTH_SVG = ROOT / "qgis" / "styles" / "north_arrow_white.svg"
OUT_PNG = ROOT / "month-03" / "week-11" / "my_reach.png"
QGZ = ROOT / "qgis" / "week11_amac_reach.qgz"

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

TITLE = "HEALTH REACH IN AMAC"
SUBTITLE = "Areas more than 2 km from a clinic"
LEGEND_TITLE = "2 km straight-line reach"
CAPTION = (
    "Warm shading shows parts of AMAC more than 2 km in a straight line from a mapped GRID3 health facility. "
    "Light sand is within that reach. "
    "Clinics without coordinates are missing, so gaps here are a floor on how far people sit from care."
)
PINNED = ("Kabusa", "Gwarinpa", "Garki 1", "Wuse", "Karu", "Nyanya 1", "City Center 1")


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
    settings.displayAll = False
    settings.obstacle = False
    settings.setUnplacedVisibility(Qgis.UnplacedLabelVisibility.NeverShow)
    settings.placementSettings().setOverlapHandling(Qgis.LabelOverlapHandling.PreventOverlap)
    fmt = QgsTextFormat()
    fmt.setFont(QFont("Helvetica", 11))
    fmt.setSize(11)
    fmt.setSizeUnit(QgsUnitTypes.RenderPoints)
    fmt.setColor(QColor(55, 50, 46))
    buf = QgsTextBufferSettings()
    buf.setEnabled(True)
    buf.setSize(1.0)
    buf.setSizeUnit(QgsUnitTypes.RenderMillimeters)
    buf.setColor(QColor(250, 250, 250))
    fmt.setBuffer(buf)
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


def _legend(layout, map_item, uncovered, wards, facilities) -> QgsLayoutItemLegend:
    legend = QgsLayoutItemLegend(layout)
    legend.setLinkedMap(map_item)
    legend.setTitle(LEGEND_TITLE)
    legend.setTitleAlignment(Qt.AlignLeft)
    legend.setStyleFont(QgsLegendStyle.Title, QFont("Arial", 13, QFont.Bold))
    legend.setStyleFont(QgsLegendStyle.Subgroup, QFont("Arial", 12))
    legend.setStyleFont(QgsLegendStyle.SymbolLabel, QFont("Arial", 12))
    legend.setFontColor(QColor(0, 0, 0))
    legend.setSymbolWidth(5.2)
    legend.setSymbolHeight(4.2)
    legend.setBoxSpace(2.5)
    legend.setLineSpacing(0.2)
    legend.setStyleMargin(QgsLegendStyle.Title, QgsLegendStyle.Bottom, 1.1)
    legend.setStyleMargin(QgsLegendStyle.Symbol, 0.3)
    legend.setStyleMargin(QgsLegendStyle.SymbolLabel, QgsLegendStyle.Left, 1.2)
    legend.setFrameEnabled(True)
    legend.setFrameStrokeColor(QColor(0, 0, 0))
    legend.setFrameStrokeWidth(QgsLayoutMeasurement(0.45, MM))
    legend.setBackgroundColor(QColor(255, 255, 255))
    legend.setBackgroundEnabled(True)
    legend.setAutoUpdateModel(False)
    root = legend.model().rootGroup()
    for child in list(root.children()):
        root.removeChildNode(child)
    for lyr in (uncovered, wards, facilities):
        node = root.addLayer(lyr)
        QgsLegendRenderer.setNodeLegendStyle(node, QgsLegendStyle.Hidden)
    legend.setZValue(20)
    layout.addLayoutItem(legend)
    rows = 3
    pad = float(legend.boxSpace())
    target_w = 62.0
    target_h = 2.0 * pad + 6.4 + rows * (float(legend.symbolHeight()) + 1.05)
    legend.setResizeToContents(True)
    legend.setReferencePoint(QgsLayoutItem.UpperLeft)
    legend.attemptMove(QgsLayoutPoint(14.0, 200.0, MM))
    legend.attemptResize(QgsLayoutSize(target_w, target_h, MM))
    legend.refresh()
    legend.adjustBoxSize()
    measured = legend.sizeWithUnits()
    mw, mh = float(measured.width()), float(measured.height())
    w = mw if 40.0 <= mw <= target_w + 8.0 else target_w
    h = min(mh if 20.0 <= mh <= target_h + 2.0 else target_h, target_h + 2.0)
    legend.setResizeToContents(False)
    legend.setReferencePoint(QgsLayoutItem.LowerLeft)
    legend.attemptResize(QgsLayoutSize(w, h, MM))
    legend.attemptMove(QgsLayoutPoint(14.0, 283.0, MM))
    print(f"  legend measured {mw:.1f}×{mh:.1f} mm → {w:.1f}×{h:.1f} mm")
    return legend


def main() -> Path:
    QgsApplication.setPrefixPath(os.environ["QGIS_PREFIX_PATH"], True)
    app = QgsApplication([], False)
    app.initQgis()

    project = QgsProject.instance()
    project.clear()
    project.setCrs(QgsCoordinateReferenceSystem(CRS))

    # Esri light grey: reliable XYZ, no API-key watermark. Place names stay off the thematic fills.
    basemap = QgsRasterLayer(
        "type=xyz&url=https://server.arcgisonline.com/ArcGIS/rest/services/"
        "Canvas/World_Light_Gray_Base/MapServer/tile/%7Bz%7D/%7By%7D/%7Bx%7D"
        "&zmax=16&zmin=0&crs=EPSG3857",
        "Esri light grey",
        "wms",
    )
    wards = QgsVectorLayer(f"{REACH}|layername=ward_reach", "Within 2 km", "ogr")
    uncovered = QgsVectorLayer(f"{REACH}|layername=uncovered", "More than 2 km", "ogr")
    facilities = QgsVectorLayer(
        f"{FAC}|layername=amac_health_facilities", "Health facility", "ogr"
    )
    for lyr in (basemap, wards, uncovered, facilities):
        if not lyr.isValid():
            raise RuntimeError(f"layer failed to load: {lyr.name()}")

    # Quiet sequential pair: sand for reach, dusty rose for gaps. No primary red/green fight.
    wards.setRenderer(
        QgsSingleSymbolRenderer(
            QgsFillSymbol.createSimple(
                {
                    "color": "232,226,214,170",
                    "outline_color": "120,114,108,140",
                    "outline_width": "0.18",
                    "outline_width_unit": "MM",
                }
            )
        )
    )
    uncovered.setRenderer(
        QgsSingleSymbolRenderer(
            QgsFillSymbol.createSimple(
                {
                    "color": "180,120,118,175",
                    "outline_color": "140,95,93,120",
                    "outline_width": "0.12",
                    "outline_width_unit": "MM",
                }
            )
        )
    )
    facilities.setRenderer(
        QgsSingleSymbolRenderer(
            QgsMarkerSymbol.createSimple(
                {
                    "name": "circle",
                    "color": "46,64,87,220",
                    "outline_color": "255,255,255,200",
                    "outline_width": "0.22",
                    "size": "1.5",
                    "size_unit": "MM",
                }
            )
        )
    )
    _ward_labels(wards)

    from qgis.core import QgsFeature

    outline = QgsVectorLayer(f"Polygon?crs={CRS}", "AMAC boundary", "memory")
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

    for lyr in (basemap, wards, uncovered, facilities, outline):
        project.addMapLayer(lyr)

    layout = QgsPrintLayout(project)
    layout.initializeDefaults()
    layout.setName("AMAC 2 km reach")
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
    map_item.setLayers([outline, facilities, uncovered, wards, basemap])
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

    legend = _legend(layout, map_item, uncovered, wards, facilities)
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
