import React, { useEffect, useRef, useState, useMemo, useCallback } from "react";
import {
    Button,
    Text,
    Card,
    Input,
    Spinner,
    Badge,
} from "@fluentui/react-components";
import { 
    InfoRegular, 
    DismissRegular, 
    ZoomInRegular, 
    ZoomOutRegular, 
    ArrowMaximizeRegular,
    SearchRegular,
} from "@fluentui/react-icons";
import * as d3 from "d3";

// Dataverse types for KM Items and Relations
type KMItem = {
    appbase_kmitemid: string;
    appbase_name: string;
    appbase_description?: string;
};

type KMItemRelation = {
    appbase_kmitemrelationid: string;
    _appbase_fromitem_value: string;
    _appbase_toitem_value: string;
};

// D3 Graph Hook with Zoom & Pan
function useD3Graph(
    items: KMItem[],
    relations: KMItemRelation[],
    onNodeClick: (item: KMItem) => void,
    selectedId: string | null,
    zoomHandlers: {
        onZoomChange: (transform: d3.ZoomTransform) => void;
        resetZoom: () => void;
    }
) {
    const ref = useRef<SVGSVGElement>(null);
    const zoomBehaviorRef = useRef<d3.ZoomBehavior<SVGSVGElement, unknown> | null>(null);

    useEffect(() => {
        if (!ref.current) return;

        // Clear previous SVG
        d3.select(ref.current).selectAll("*").remove();

        if (items.length === 0) return;

        // Prepare graph data
        const nodes = items.map((item) => ({
            ...item,
            id: item.appbase_kmitemid,
            name: item.appbase_name,
        }));
        
        // FIXED: Use the correct field names for lookup values
        const links = relations
            .filter(rel => rel._appbase_fromitem_value && rel._appbase_toitem_value)
            .map((rel) => ({
                source: rel._appbase_fromitem_value,
                target: rel._appbase_toitem_value,
            }));

        const width = ref.current.parentElement
            ? ref.current.parentElement.clientWidth
            : 600;
        const height = ref.current.parentElement
            ? ref.current.parentElement.clientHeight
            : 400;

        // D3 force simulation
        const simulation = d3
            .forceSimulation(nodes as any)
            .force(
                "link",
                d3.forceLink(links).id((d: any) => d.id).distance(120)
            )
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(40))
            .stop();

        // Run simulation for fixed steps
        for (let i = 0; i < 100; ++i) simulation.tick();

        // Get updated links with node objects
        const updatedLinks = (simulation.force("link") as d3.ForceLink<any, any>).links();

        // SVG setup
        const svg = d3
            .select(ref.current)
            .attr("width", width)
            .attr("height", height)
            .attr("style", "max-width:100%;height:auto;display:block;cursor:grab;");

        // Create zoom behavior
        const zoom = d3.zoom<SVGSVGElement, unknown>()
            .scaleExtent([0.1, 4])
            .on("zoom", (event) => {
                zoomGroup.attr("transform", event.transform);
                zoomHandlers.onZoomChange(event.transform);
            });

        zoomBehaviorRef.current = zoom;
        svg.call(zoom);

        // Create container group for zoom
        const zoomGroup = svg.append("g").attr("class", "zoom-group");

        // Draw arrow marker
        svg
            .append("defs")
            .append("marker")
            .attr("id", "arrow")
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 20)
            .attr("refY", 0)
            .attr("markerWidth", 6)
            .attr("markerHeight", 6)
            .attr("orient", "auto")
            .append("path")
            .attr("d", "M0,-5L10,0L0,5")
            .attr("fill", "#999999");

        // Draw links
        const linkElements = zoomGroup
            .append("g")
            .attr("class", "links")
            .selectAll("line")
            .data(updatedLinks)
            .enter()
            .append("line")
            .attr("x1", (d: any) => d.source.x)
            .attr("y1", (d: any) => d.source.y)
            .attr("x2", (d: any) => d.target.x)
            .attr("y2", (d: any) => d.target.y)
            .attr("stroke", "#CCCCCC")
            .attr("stroke-width", 2)
            .attr("marker-end", "url(#arrow)")
            .attr("opacity", 0.6);

        // Create tooltip
        const tooltip = d3.select("body")
            .append("div")
            .attr("class", "graph-tooltip")
            .style("position", "absolute")
            .style("visibility", "hidden")
            .style("background", "#323130")
            .style("color", "#FFFFFF")
            .style("padding", "8px 12px")
            .style("border-radius", "6px")
            .style("font-size", "14px")
            .style("font-weight", "500")
            .style("box-shadow", "0 4px 12px rgba(0,0,0,0.2)")
            .style("pointer-events", "none")
            .style("z-index", "1000")
            .style("max-width", "200px");

        // Draw nodes
        const nodeGroup = zoomGroup
            .append("g")
            .attr("class", "nodes")
            .selectAll("g")
            .data(nodes)
            .enter()
            .append("g")
            .attr("transform", (d: any) => `translate(${d.x},${d.y})`)
            .attr("tabindex", 0)
            .attr("role", "button")
            .attr("aria-label", (d: any) => d.name)
            .attr("cursor", "pointer")
            .on("click", (event: any, d: KMItem) => {
                event.stopPropagation();
                onNodeClick(d);
            })
            .on("mouseover", function (event: any, d: any) {
                // Highlight node
                d3.select(this)
                    .select("circle")
                    .attr("fill", "#D0E7FF")
                    .attr("stroke", "#0078D4")
                    .attr("stroke-width", 4);

                // Highlight connected links
                linkElements
                    .attr("stroke", (l: any) => {
                        if (l.source.id === d.id || l.target.id === d.id) {
                            return "#0078D4";
                        }
                        return "#CCCCCC";
                    })
                    .attr("stroke-width", (l: any) => {
                        if (l.source.id === d.id || l.target.id === d.id) {
                            return 3;
                        }
                        return 2;
                    })
                    .attr("opacity", (l: any) => {
                        if (l.source.id === d.id || l.target.id === d.id) {
                            return 1;
                        }
                        return 0.3;
                    });

                // Show tooltip
                tooltip
                    .style("visibility", "visible")
                    .html(`
                        <div><strong>${d.name}</strong></div>
                        ${d.appbase_description ? `<div style="margin-top:4px;font-size:12px;opacity:0.9;">${d.appbase_description.substring(0, 100)}${d.appbase_description.length > 100 ? '...' : ''}</div>` : ''}
                    `);
            })
            .on("mousemove", function (event: any) {
                tooltip
                    .style("top", (event.pageY - 10) + "px")
                    .style("left", (event.pageX + 10) + "px");
            })
            .on("mouseout", function (event: any, d: any) {
                // Reset node
                d3.select(this)
                    .select("circle")
                    .attr("fill", selectedId === d.id ? "#0078D4" : "#E1DFDD")
                    .attr("stroke", selectedId === d.id ? "#004578" : "#8A8886")
                    .attr("stroke-width", selectedId === d.id ? 4 : 2);

                // Reset links
                linkElements
                    .attr("stroke", "#CCCCCC")
                    .attr("stroke-width", 2)
                    .attr("opacity", 0.6);

                // Hide tooltip
                tooltip.style("visibility", "hidden");
            });

        // Node circles with shadow
        nodeGroup
            .append("circle")
            .attr("r", 36)
            .attr("fill", (d: any) => selectedId === d.id ? "#0078D4" : "#E1DFDD")
            .attr("stroke", (d: any) => selectedId === d.id ? "#004578" : "#8A8886")
            .attr("stroke-width", (d: any) => selectedId === d.id ? 4 : 2)
            .attr("filter", "drop-shadow(0 2px 4px rgba(0,0,0,0.15))")
            .style("transition", "all 0.3s ease");

        // Node labels
        nodeGroup
            .append("text")
            .attr("text-anchor", "middle")
            .attr("dy", "0.35em")
            .attr("font-size", "14px")
            .attr("font-weight", "600")
            .attr("fill", (d: any) => selectedId === d.id ? "#FFFFFF" : "#323130")
            .text((d: any) => {
                // Truncate long names
                const name = d.name || "";
                return name.length > 12 ? name.substring(0, 10) + "..." : name;
            })
            .attr("pointer-events", "none");

        // Accessibility: focus ring
        nodeGroup
            .on("focus", function (event: any, d: KMItem) {
                d3.select(this)
                    .select("circle")
                    .attr("stroke", "#FFB900")
                    .attr("stroke-width", 4);
            })
            .on("blur", function (event: any, d: KMItem) {
                d3.select(this)
                    .select("circle")
                    .attr("stroke", selectedId === d.id ? "#004578" : "#8A8886")
                    .attr("stroke-width", selectedId === d.id ? 4 : 2);
            });

        // Zoom to fit on initial load
        const bounds = zoomGroup.node()?.getBBox();
        if (bounds && bounds.width > 0 && bounds.height > 0) {
            const dx = bounds.width;
            const dy = bounds.height;
            const x = bounds.x + dx / 2;
            const y = bounds.y + dy / 2;
            const scale = Math.min(3, 0.9 / Math.max(dx / width, dy / height));
            const translate = [width / 2 - scale * x, height / 2 - scale * y];

            svg.call(
                zoom.transform as any,
                d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale)
            );
        }

        // Store reset function
        zoomHandlers.resetZoom = () => {
            if (bounds && bounds.width > 0) {
                const dx = bounds.width;
                const dy = bounds.height;
                const x = bounds.x + dx / 2;
                const y = bounds.y + dy / 2;
                const scale = Math.min(3, 0.9 / Math.max(dx / width, dy / height));
                const translate = [width / 2 - scale * x, height / 2 - scale * y];

                svg.transition()
                    .duration(750)
                    .call(
                        zoom.transform as any,
                        d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale)
                    );
            }
        };

        // Clean up on unmount
        return () => {
            simulation.stop();
            tooltip.remove();
            d3.select(ref.current).selectAll("*").remove();
        };
    }, [items, relations, onNodeClick, selectedId]);

    return { ref, zoomBehavior: zoomBehaviorRef.current };
}

// KM Item Details Sidebar
const KMItemDetailsSidebar = React.memo(({
    item,
    onClose,
    t,
    relatedItems,
}: {
    item: KMItem | null;
    onClose: () => void;
    t: (key: string) => string;
    relatedItems: KMItem[];
}) => {
    if (!item) return null;
    
    return (
        <aside
            aria-label={t("details")}
            style={{
                width: "320px",
                minWidth: "240px",
                maxWidth: "100vw",
                background: "#F3F2F1",
                borderRadius: "12px",
                boxShadow: "0 4px 16px rgba(0,0,0,0.12)",
                padding: "24px 20px",
                marginLeft: "24px",
                display: "flex",
                flexDirection: "column",
                boxSizing: "border-box",
                height: "100%",
                alignSelf: "stretch",
                position: "relative",
                zIndex: 2,
                animation: "slideIn 0.3s ease-out",
            }}
        >
            <style>
                {`
                    @keyframes slideIn {
                        from {
                            opacity: 0;
                            transform: translateX(20px);
                        }
                        to {
                            opacity: 1;
                            transform: translateX(0);
                        }
                    }
                `}
            </style>
            <div style={{ display: "flex", alignItems: "center", marginBottom: 16 }}>
                <InfoRegular fontSize="24px" style={{ marginInlineEnd: 8, color: "#0078D4" }} />
                <Text as="h2" size={600} weight="semibold" id="km-details-title">
                    {t("details")}
                </Text>
                <Button
                    appearance="subtle"
                    icon={<DismissRegular fontSize="20px" />}
                    onClick={onClose}
                    style={{
                        marginInlineStart: "auto",
                        marginLeft: "auto",
                        marginRight: 0,
                        padding: 0,
                        minWidth: 32,
                        minHeight: 32,
                    }}
                    aria-label={t("close")}
                />
            </div>
            <Card
                style={{
                    marginTop: 8,
                    padding: 16,
                    borderRadius: "8px",
                    boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
                    background: "#FFFFFF",
                }}
            >
                <Text size={500} weight="semibold" block style={{ color: "#323130" }}>
                    {item.appbase_name}
                </Text>
                <Text size={400} block style={{ marginTop: 8, color: "#605E5C", lineHeight: 1.5 }}>
                    {item.appbase_description || t("noDescription")}
                </Text>
            </Card>
            
            {/* Related Items Section */}
            {relatedItems.length > 0 && (
                <Card
                    style={{
                        marginTop: 16,
                        padding: 16,
                        borderRadius: "8px",
                        boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
                        background: "#FFFFFF",
                        flex: 1,
                        overflow: "auto",
                    }}
                >
                    <div style={{ display: "flex", alignItems: "center", marginBottom: 12 }}>
                        <Text size={400} weight="semibold" style={{ color: "#323130" }}>
                            {t("relatedItems")}
                        </Text>
                        <Badge 
                            appearance="filled" 
                            color="informative"
                            style={{ marginLeft: 8 }}
                        >
                            {relatedItems.length}
                        </Badge>
                    </div>
                    <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                        {relatedItems.map((relatedItem) => (
                            <div
                                key={relatedItem.appbase_kmitemid}
                                style={{
                                    padding: "8px 12px",
                                    background: "#F5F5F5",
                                    borderRadius: "6px",
                                    borderLeft: "3px solid #0078D4",
                                }}
                            >
                                <Text size={300} weight="semibold" block style={{ color: "#323130" }}>
                                    {relatedItem.appbase_name}
                                </Text>
                            </div>
                        ))}
                    </div>
                </Card>
            )}
        </aside>
    );
});

// Main Component
const GeneratedComponent = ({ dataApi }: { dataApi: any }) => {
    // Localization setup (inside component)
    const langMap: Record<number, { code: string; name: string; isRtl: boolean }> = {
        1033: { code: "en-US", name: "English (United States)", isRtl: false },
    };
    const language = React.useMemo(() => {
        const uiLanguageId =
            (typeof Xrm !== "undefined" &&
                Xrm.Utility?.getGlobalContext()?.userSettings?.languageId) || 1033;
        return langMap[uiLanguageId]?.code || "en-US";
    }, []);
    const translations: Record<string, Record<string, string>> = {
        "en-US": {
            title: "Knowledge Management Graph",
            details: "Details",
            close: "Close",
            noDescription: "No description available.",
            graphInstructions: "Click nodes to view details. Use mouse wheel to zoom, drag to pan.",
            search: "Search knowledge items...",
            zoomIn: "Zoom In",
            zoomOut: "Zoom Out",
            zoomReset: "Reset Zoom",
            loading: "Loading knowledge graph...",
            noData: "No knowledge items found. Create some items to see them visualized here.",
            nodes: "Nodes",
            connections: "Connections",
            relatedItems: "Related Items",
            errorLoading: "Error loading data. Please try again.",
        },
    };
    const t = (key: string): string =>
        translations[language]?.[key] || translations["en-US"]?.[key] || key;

    const [items, setItems] = useState<KMItem[]>([]);
    const [relations, setRelations] = useState<KMItemRelation[]>([]);
    const [selectedItem, setSelectedItem] = useState<KMItem | null>(null);
    const [searchQuery, setSearchQuery] = useState("");
    const [isLoading, setIsLoading] = useState(true);
    const [hasError, setHasError] = useState(false);
    const [zoomTransform, setZoomTransform] = useState<d3.ZoomTransform | null>(null);

    // Zoom handlers
    const zoomHandlersRef = useRef({
        onZoomChange: (transform: d3.ZoomTransform) => {
            setZoomTransform(transform);
        },
        resetZoom: () => {},
    });

    // Fetch KM Items from Dataverse
    useEffect(() => {
        const fetchItems = async () => {
            try {
                setIsLoading(true);
                setHasError(false);
                const result = await dataApi.queryTable("appbase_kmitems", {
                    select: ["appbase_kmitemid", "appbase_name", "appbase_description"],
                    pageSize: 100,
                    orderBy: "appbase_name asc",
                });
                setItems(result.rows || []);
            } catch (err) {
                console.error("Error fetching KM items:", err);
                setHasError(true);
                setItems([]);
            } finally {
                setIsLoading(false);
            }
        };
        fetchItems();
    }, [dataApi]);

    // Fetch KM Item Relations from Dataverse
    useEffect(() => {
        const fetchRelations = async () => {
            try {
                // FIXED: Select the correct lookup value fields
                const result = await dataApi.queryTable("appbase_kmitemrelation", {
                    select: ["appbase_kmitemrelationid", "_appbase_fromitem_value", "_appbase_toitem_value"],
                    pageSize: 100,
                });
                setRelations(result.rows || []);
            } catch (err) {
                console.error("Error fetching KM item relations:", err);
                setRelations([]);
            }
        };
        fetchRelations();
    }, [dataApi]);

    // Filter items based on search query
    const filteredItems = useMemo(() => {
        if (!searchQuery) return items;
        const query = searchQuery.toLowerCase();
        return items.filter(
            (item) =>
                item.appbase_name?.toLowerCase().includes(query) ||
                item.appbase_description?.toLowerCase().includes(query)
        );
    }, [items, searchQuery]);

    // Get related items for selected item
    const relatedItems = useMemo(() => {
        if (!selectedItem) return [];
        const relatedIds = new Set<string>();
        
        relations.forEach((rel) => {
            if (rel._appbase_fromitem_value === selectedItem.appbase_kmitemid) {
                relatedIds.add(rel._appbase_toitem_value);
            }
            if (rel._appbase_toitem_value === selectedItem.appbase_kmitemid) {
                relatedIds.add(rel._appbase_fromitem_value);
            }
        });
        
        return items.filter((item) => relatedIds.has(item.appbase_kmitemid));
    }, [selectedItem, items, relations]);

    // D3 graph ref
    const graphResult = useD3Graph(
        filteredItems,
        relations,
        (item) => {
            setSelectedItem(item);
        },
        selectedItem ? selectedItem.appbase_kmitemid : null,
        zoomHandlersRef.current
    );

    // Zoom control handlers
    const handleZoomIn = useCallback(() => {
        if (graphResult.ref.current && graphResult.zoomBehavior) {
            d3.select(graphResult.ref.current)
                .transition()
                .duration(300)
                .call(graphResult.zoomBehavior.scaleBy as any, 1.3);
        }
    }, [graphResult]);

    const handleZoomOut = useCallback(() => {
        if (graphResult.ref.current && graphResult.zoomBehavior) {
            d3.select(graphResult.ref.current)
                .transition()
                .duration(300)
                .call(graphResult.zoomBehavior.scaleBy as any, 1 / 1.3);
        }
    }, [graphResult]);

    const handleZoomReset = useCallback(() => {
        zoomHandlersRef.current.resetZoom();
    }, []);

    // Responsive layout: flex row for graph + sidebar
    return (
        <div
            dir="ltr"
            style={{
                flexGrow: 1,
                alignSelf: "stretch",
                width: "100%",
                height: "100%",
                minHeight: 0,
                padding: "24px",
                boxSizing: "border-box",
                display: "flex",
                flexDirection: "column",
                background: "#FAFAFA",
            }}
        >
            {/* Header */}
            <header
                style={{
                    marginBottom: "16px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    flexWrap: "wrap",
                    gap: "16px",
                }}
            >
                <div>
                    <Text as="h1" size={700} weight="semibold" block style={{ marginBottom: "4px" }}>
                        {t("title")}
                    </Text>
                    <Text size={300} style={{ color: "#605E5C" }}>
                        {t("graphInstructions")}
                    </Text>
                </div>
                
                {/* Statistics */}
                {!isLoading && !hasError && (
                    <div style={{ display: "flex", gap: "16px", alignItems: "center" }}>
                        <div style={{ textAlign: "center" }}>
                            <Text size={600} weight="semibold" block style={{ color: "#0078D4" }}>
                                {filteredItems.length}
                            </Text>
                            <Text size={200} style={{ color: "#605E5C" }}>
                                {t("nodes")}
                            </Text>
                        </div>
                        <div style={{ textAlign: "center" }}>
                            <Text size={600} weight="semibold" block style={{ color: "#0078D4" }}>
                                {relations.length}
                            </Text>
                            <Text size={200} style={{ color: "#605E5C" }}>
                                {t("connections")}
                            </Text>
                        </div>
                    </div>
                )}
            </header>

            {/* Search Bar */}
            {!isLoading && !hasError && items.length > 0 && (
                <div style={{ marginBottom: "16px", maxWidth: "400px" }}>
                    <Input
                        contentBefore={<SearchRegular />}
                        placeholder={t("search")}
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        style={{ width: "100%" }}
                    />
                </div>
            )}

            {/* Graph + Sidebar Area */}
            <section
                style={{
                    flex: 1,
                    minHeight: 0,
                    background: "#FFFFFF",
                    borderRadius: "12px",
                    boxShadow: "0 2px 8px rgba(0,0,0,0.06)",
                    padding: "16px",
                    display: "flex",
                    flexDirection: "row",
                    overflow: "hidden",
                    position: "relative",
                }}
                aria-label={t("title")}
            >
                {/* Loading State */}
                {isLoading && (
                    <div
                        style={{
                            flex: 1,
                            display: "flex",
                            flexDirection: "column",
                            alignItems: "center",
                            justifyContent: "center",
                            gap: "16px",
                        }}
                    >
                        <Spinner size="large" />
                        <Text size={400} style={{ color: "#605E5C" }}>
                            {t("loading")}
                        </Text>
                    </div>
                )}

                {/* Error State */}
                {!isLoading && hasError && (
                    <div
                        style={{
                            flex: 1,
                            display: "flex",
                            flexDirection: "column",
                            alignItems: "center",
                            justifyContent: "center",
                            gap: "16px",
                        }}
                    >
                        <Text size={500} weight="semibold" style={{ color: "#A4262C" }}>
                            {t("errorLoading")}
                        </Text>
                    </div>
                )}

                {/* Empty State */}
                {!isLoading && !hasError && items.length === 0 && (
                    <div
                        style={{
                            flex: 1,
                            display: "flex",
                            flexDirection: "column",
                            alignItems: "center",
                            justifyContent: "center",
                            gap: "16px",
                        }}
                    >
                        <InfoRegular fontSize="48px" style={{ color: "#8A8886" }} />
                        <Text size={400} style={{ color: "#605E5C", textAlign: "center", maxWidth: "400px" }}>
                            {t("noData")}
                        </Text>
                    </div>
                )}

                {/* Graph SVG */}
                {!isLoading && !hasError && items.length > 0 && (
                    <>
                        <div
                            style={{
                                flex: 1,
                                minWidth: 0,
                                minHeight: 0,
                                display: "flex",
                                flexDirection: "column",
                                alignItems: "stretch",
                                justifyContent: "stretch",
                                position: "relative",
                            }}
                        >
                            {/* Zoom Controls */}
                            <div
                                style={{
                                    position: "absolute",
                                    top: "16px",
                                    right: "16px",
                                    zIndex: 10,
                                    display: "flex",
                                    flexDirection: "column",
                                    gap: "8px",
                                    background: "#FFFFFF",
                                    padding: "8px",
                                    borderRadius: "8px",
                                    boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
                                }}
                            >
                                <Button
                                    appearance="subtle"
                                    icon={<ZoomInRegular />}
                                    onClick={handleZoomIn}
                                    aria-label={t("zoomIn")}
                                    title={t("zoomIn")}
                                    size="small"
                                />
                                <Button
                                    appearance="subtle"
                                    icon={<ZoomOutRegular />}
                                    onClick={handleZoomOut}
                                    aria-label={t("zoomOut")}
                                    title={t("zoomOut")}
                                    size="small"
                                />
                                <Button
                                    appearance="subtle"
                                    icon={<ArrowMaximizeRegular />}
                                    onClick={handleZoomReset}
                                    aria-label={t("zoomReset")}
                                    title={t("zoomReset")}
                                    size="small"
                                />
                            </div>

                            <svg
                                ref={graphResult.ref}
                                style={{
                                    width: "100%",
                                    height: "100%",
                                    minHeight: 320,
                                    display: "block",
                                    borderRadius: "8px",
                                    background: "#F9F9F9",
                                    boxSizing: "border-box",
                                }}
                                aria-label={t("title")}
                            />
                        </div>
                        {/* Details Sidebar */}
                        <KMItemDetailsSidebar
                            item={selectedItem}
                            onClose={() => setSelectedItem(null)}
                            t={t}
                            relatedItems={relatedItems}
                        />
                    </>
                )}
            </section>
        </div>
    );
};

export default GeneratedComponent;