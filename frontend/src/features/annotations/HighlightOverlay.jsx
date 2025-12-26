import React from "react";
import useAnnotationStore from "../../stores/annotationStore";
import { cn } from "../../lib/utils";

/**
 * Highlight Overlay Component
 * Displays annotation markers on the PDF page
 */

export default function HighlightOverlay({ pageNumber, scale, currentLesson }) {
  const getAnnotationsByPage = useAnnotationStore(
    (state) => state.getAnnotationsByPage
  );
  const setViewingAnnotation = useAnnotationStore(
    (state) => state.setViewingAnnotation
  );
  const setActivePanel = useAnnotationStore((state) => state.setActivePanel);

  const annotations = getAnnotationsByPage(currentLesson?.id, pageNumber);

  const handleHighlightClick = (annotation) => {
    setViewingAnnotation(annotation);
    if (annotation.type === "ai") {
      setActivePanel("history");
    } else {
      setActivePanel("history");
    }
  };

  return (
    <div className="absolute inset-0 pointer-events-none z-10">
      {annotations.map((annotation, index) => {
        const isNote = annotation.type === "note";
        const highlightColor = isNote
          ? "bg-emerald-100/90 hover:bg-emerald-200/90 border-emerald-500"
          : "bg-rose-100/90 hover:bg-rose-200/90 border-rose-700";

        const tagColor = isNote
          ? "bg-emerald-600 text-white"
          : "bg-primary text-white";

        const position = annotation.position || {
          x: 100 + (index % 3) * 200,
          y: 100 + Math.floor(index / 3) * 150,
        };

        return (
          <div
            key={annotation.id}
            className="absolute pointer-events-auto"
            style={{
              left: `${position.x}px`,
              top: `${position.y}px`,
              transform: "translate(-50%, -50%)",
            }}
          >
            <div
              className={cn(
                "relative rounded-lg shadow-lg cursor-pointer transition-all hover:shadow-xl hover:scale-105",
                "border-2 p-3 min-w-[120px] max-w-[200px]",
                highlightColor
              )}
              onClick={() => handleHighlightClick(annotation)}
            >
              <div
                className={cn(
                  "absolute -top-2 -left-2 px-2 py-0.5 rounded-full text-xs font-bold shadow-md",
                  tagColor
                )}
              >
                {isNote ? " Note" : " AI"}
              </div>

              <div className="mt-2">
                <div className="text-xs font-semibold line-clamp-2 text-gray-800">
                  {isNote ? annotation.heading : annotation.action}
                </div>
                <div className="text-xs text-gray-600 line-clamp-2 mt-1">
                  {annotation.text?.substring(0, 50)}...
                </div>
              </div>

              <div className="text-[10px] text-gray-500 mt-1">
                Page {annotation.pageNumber}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
