import {
  Box,
  Button,
  Collapse,
  IconButton,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  Tooltip,
  Typography,
} from "@mui/material";
import {
  ChartData,
  ChartDataset,
  Chart as ChartJS,
  ChartOptions,
  registerables,
} from "chart.js";
import annotationPlugin from "chartjs-plugin-annotation";
import "chartjs-plugin-dragdata";
import zoomPlugin from "chartjs-plugin-zoom";
import React, { useCallback, useEffect, useMemo, useState } from "react";
import { Line } from "react-chartjs-2";
import readXlsxFile from "read-excel-file";
import FileUploadDownloadButton from "./FileUploadDownloadButton";
import { Point, Step, StepData } from "./Types/Step";

import { ArrowBack, ArrowForward, MenuBook } from "@mui/icons-material";
import { calculateLine } from "../api/CalculateLineService";
import classes from "./ReactChartJs.module.scss";

ChartJS.register(...registerables, annotationPlugin, zoomPlugin);

const ReactChartJs: React.FC = () => {
  const [redPoints, setRedPoints] = useState(7);
  const [bluePoints, setBluePoints] = useState(5);
  const [redData, setRedData] = useState<Point[]>([]);
  const [blueData, setBlueData] = useState<Point[]>([]);
  const [graphBounds, setGraphBounds] = useState({
    minX: 0,
    minY: 0,
    maxX: 10,
    maxY: 10,
  });

  const [isCalculating, setIsCalculating] = useState(false);

  const [hasError, setHasError] = useState(false);
  // State for Teach Mode Steps
  const [stepsTaken, setStepsTaken] = useState<Step[]>([]);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [finalCut, setFinalCut] = useState<{
    slope: number;
    intercept: number;
  } | null>(null);
  const [currentStepData, setCurrentStepData] = useState<StepData | null>(null);

  // State for Teach Mode
  const [teachMode, setTeachMode] = useState(false);

  useEffect(() => {
    // Assuming stepsTaken is populated from the API or a similar source
    if (stepsTaken.length > 0) {
      setCurrentStepData(stepsTaken[currentStepIndex]?.data);
    }
  }, [currentStepIndex, stepsTaken]);

  const randomiseData = () => {
    setRedData(
      Array.from({ length: redPoints }, () => ({
        x: Math.random() * 20 - 10 + Math.random() * 0.0001,
        y: Math.random() * 20 - 10 + Math.random() * 0.0001,
      }))
    );
    setBlueData(
      Array.from({ length: bluePoints }, () => ({
        x: Math.random() * 20 - 10 + Math.random() * 0.0001,
        y: Math.random() * 20 - 10 + Math.random() * 0.0001,
      }))
    );
  };

  const memoizedCalculateLine = useCallback(() => {
    calculateLine(
      redData,
      blueData,
      setIsCalculating,
      setHasError,
      setStepsTaken,
      setFinalCut,
      teachMode
    );
  }, [
    redData,
    blueData,
    teachMode,
    setIsCalculating,
    setHasError,
    setStepsTaken,
    setFinalCut,
  ]);

  const chartDataSets = useMemo<ChartData<"line">>(() => {
    const datasets: ChartDataset<"line">[] = [];

    datasets.push({
      data: redData,
      label: "Red Points",
      backgroundColor: "rgba(255, 99, 132, 0.5)",
      borderColor: "rgba(255, 99, 132, 1)",
      pointRadius: 10,
      showLine: false, // Scatter points
    });

    datasets.push({
      data: blueData,
      label: "Blue Points",
      backgroundColor: "rgba(54, 162, 235, 0.5)",
      borderColor: "rgba(54, 162, 235, 1)",
      pointRadius: 10,
      showLine: false,
    });

    // Add line dataset if finalCut exists
    if (finalCut) {
      const lineData: Point[] = [
        {
          x: graphBounds.minX,
          y: finalCut.slope * graphBounds.minX + finalCut.intercept,
        },
        {
          x: graphBounds.maxX,
          y: finalCut.slope * graphBounds.maxX + finalCut.intercept,
        },
      ];

      datasets.push({
        label: "Ham Sandwich Cut",
        data: lineData,
        borderColor: "rgba(75, 192, 192, 1)",
        borderWidth: 2,
        showLine: true,
        fill: false,
        pointRadius: 0, // Hide points for the ham cut line
      });
    }

    if (currentStepData) {
      // Add interval median points with color-specific styling
      if (currentStepData.intervalMedians) {
        datasets.push({
          label: "Interval Medians",
          data: currentStepData.intervalMedians,
          backgroundColor: currentStepData.intervalMedians.map((point) =>
            point.color === "red"
              ? "rgba(255, 99, 132, 1)"
              : "rgba(54, 162, 235, 1)"
          ),
          borderColor: currentStepData.intervalMedians.map((point) =>
            point.color === "red"
              ? "rgba(255, 99, 132, 1)"
              : "rgba(54, 162, 235, 1)"
          ),
          pointStyle: "star",
          pointRadius: 8,
          showLine: false,
        });
      }

      // Add dual lines if they exist, but group them into a single dataset per color
      if (currentStepData.dualLines) {
        ["red", "blue"].forEach((color) => {
          const dualLines =
            currentStepData.dualLines?.[color as "red" | "blue"];
          if (dualLines) {
            const allDualLinePoints: Point[] = dualLines.flatMap((line) => [
              { x: graphBounds.minX, y: line.m * graphBounds.minX + line.b },
              { x: graphBounds.maxX, y: line.m * graphBounds.maxX + line.b },
            ]);
            datasets.push({
              label: `${
                color.charAt(0).toUpperCase() + color.slice(1)
              } Dual Lines`,
              data: allDualLinePoints,
              borderColor:
                color === "red"
                  ? "rgba(255, 99, 132, 1)"
                  : "rgba(54, 162, 235, 1)",
              borderWidth: 1,
              showLine: true,
              fill: false,
              pointRadius: 0,
            });
          }
        });
      }

      // Add interval bounds if they exist
      if (currentStepData.interval) {
        datasets.push({
          label: "Interval Start",
          data: [
            { x: currentStepData.interval.start, y: graphBounds.minY },
            { x: currentStepData.interval.start, y: graphBounds.maxY },
          ],
          borderColor: "rgba(153, 102, 255, 1)",
          borderWidth: 2,
          showLine: true,
          fill: false,
          pointRadius: 0,
        });

        datasets.push({
          label: "Interval End",
          data: [
            { x: currentStepData.interval.end, y: graphBounds.minY },
            { x: currentStepData.interval.end, y: graphBounds.maxY },
          ],
          borderColor: "rgba(153, 102, 255, 1)",
          borderWidth: 2,
          showLine: true,
          fill: false,
          pointRadius: 0,
        });
      }

      // Add Ham Sandwich Cut from currentStepData.cut if it exists
      if (currentStepData.cut) {
        const cutData: Point[] = [
          {
            x: graphBounds.minX,
            y:
              currentStepData.cut.slope * graphBounds.minX +
              currentStepData.cut.intercept,
          },
          {
            x: graphBounds.maxX,
            y:
              currentStepData.cut.slope * graphBounds.maxX +
              currentStepData.cut.intercept,
          },
        ];

        datasets.push({
          label: "Ham Sandwich Cut",
          data: cutData,
          borderColor: "rgba(0, 255, 127, 1)",
          borderWidth: 2,
          showLine: true,
          fill: false,
          pointRadius: 0, // Hide points for the ham cut line
        });

        // dual point of line y = mx + b is (x, -b)
        const dualPoint = {
          x: currentStepData.cut.slope,
          y: -currentStepData.cut.intercept,
        } as Point;

        datasets.push({
          label: "Ham Sandwich Cut Dual Point",
          data: [dualPoint],
          backgroundColor: "rgba(0, 255, 127, 1)",
          borderColor: "rgba(0, 255, 127, 1)",
          pointRadius: 10,
          showLine: false,
        });
      }
    }

    return { datasets };
  }, [redData, blueData, finalCut, currentStepData, graphBounds]);

  const chartData: ChartData<"line"> = chartDataSets;

  // Calculate gprah bounds
  useEffect(() => {
    const allPoints = [
      ...redData,
      ...blueData,
      ...(currentStepData?.intervalMedians || []),
      ...(currentStepData?.dualLines?.red?.flatMap((line) => [
        { x: graphBounds.minX, y: line.m * graphBounds.minX + line.b },
        { x: graphBounds.maxX, y: line.m * graphBounds.maxX + line.b },
      ]) || []),
      ...(currentStepData?.dualLines?.blue?.flatMap((line) => [
        { x: graphBounds.minX, y: line.m * graphBounds.minX + line.b },
        { x: graphBounds.maxX, y: line.m * graphBounds.maxX + line.b },
      ]) || []),
      ...(currentStepData?.cut
        ? [
            {
              x: graphBounds.minX,
              y:
                currentStepData.cut.slope * graphBounds.minX +
                currentStepData.cut.intercept,
            },
            {
              x: graphBounds.maxX,
              y:
                currentStepData.cut.slope * graphBounds.maxX +
                currentStepData.cut.intercept,
            },
          ]
        : []),
    ];

    if (currentStepData?.interval) {
      allPoints.push(
        { x: currentStepData.interval.start, y: graphBounds.minY },
        { x: currentStepData.interval.start, y: graphBounds.maxY },
        { x: currentStepData.interval.end, y: graphBounds.minY },
        { x: currentStepData.interval.end, y: graphBounds.maxY }
      );
    }

    if (currentStepData?.cut) {
      const dualPoint = {
        x: currentStepData.cut.slope,
        y: -currentStepData.cut.intercept,
      };

      allPoints.push(dualPoint);
    }

    if (allPoints.length > 0) {
      const padding = 1;
      const minX = Math.floor(
        Math.min(...allPoints.map((p) => p.x), 0) - padding
      );
      const maxX = Math.ceil(
        Math.max(...allPoints.map((p) => p.x), 10) + padding
      );
      const minY = Math.floor(
        Math.min(...allPoints.map((p) => p.y), 0) - padding
      );
      const maxY = Math.ceil(
        Math.max(...allPoints.map((p) => p.y), 10) + padding
      );

      setGraphBounds({ minX, maxX, minY, maxY });
    }
  }, [redData, blueData, currentStepData, finalCut]);

  // initial random data
  useEffect(() => {
    randomiseData();
  }, []);

  useEffect(() => {
    memoizedCalculateLine();
  }, [redData, blueData]);

  useEffect(() => {
    setStepsTaken([]);
    setCurrentStepIndex(0);
    setCurrentStepData(null);
    setFinalCut(null);
    memoizedCalculateLine();
  }, [teachMode]);

  useEffect(() => {
    if (currentStepIndex) {
      setCurrentStepData(stepsTaken[currentStepIndex]?.data);
    }
  }, [currentStepIndex, stepsTaken]);

  const options: ChartOptions<"line"> = {
    maintainAspectRatio: false,
    plugins: {
      dragData: {
        round: 3,
        dragX: true,
        dragY: true,
        onDragEnd: () => {
          memoizedCalculateLine(); // Recalculate on drag end
          if (teachMode) {
            setCurrentStepIndex(0);
          }
        },
      },
      zoom: {
        zoom: {
          wheel: {
            enabled: true,
            modifierKey: "ctrl",
          },
          pinch: {
            enabled: true,
          },
          mode: "xy",
        },
        pan: {
          enabled: true,
          mode: "xy",
          modifierKey: "ctrl",
        },
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            const raw = context.raw as { x: number; y: number };
            if (context.dataset.label === "Ham Sandwich Cut") {
              return `Cut: y = ${raw.y.toFixed(2)}`;
            } else if (context.dataset.label?.includes("Dual Lines")) {
              return `Dual Line: y = ${raw.y.toFixed(2)}`;
            } else if (context.dataset.label?.includes("Interval")) {
              return `Interval: x = ${raw.x.toFixed(2)}`;
            } else {
              return `${context.dataset.label}: (${raw.x.toFixed(
                2
              )}, ${raw.y.toFixed(2)})`;
            }
          },
        },
      },
    },
    scales: {
      x: {
        type: "linear",
        min: graphBounds.minX,
        max: graphBounds.maxX,
      },
      y: {
        type: "linear",
        min: graphBounds.minY,
        max: graphBounds.maxY,
      },
    },
  };

  const handleFileUpload = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (file.name.endsWith(".json")) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const fileContent = e.target?.result as string;
        const jsonData = JSON.parse(fileContent);
        console.log(jsonData);
        setRedData(jsonData.redPoints);
        setBlueData(jsonData.bluePoints);
        setRedPoints(jsonData.redPoints.length);
        setBluePoints(jsonData.bluePoints.length);
      };
      reader.readAsText(file);
    } else if (file.name.endsWith(".csv")) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const fileContent = e.target?.result as string;
        const parsedData = fileContent.split("\n").map((row) => row.split(","));
        const redFileData: Point[] = [];
        const blueFileData: Point[] = [];
        parsedData.slice(1).forEach(([x, y, type]) => {
          const point = { x: parseFloat(x), y: parseFloat(y) };
          if (type?.trim().toLowerCase() === "red") {
            redFileData.push(point);
          } else if (type?.trim().toLowerCase() === "blue") {
            blueFileData.push(point);
          }
        });
        setRedData(redFileData);
        setBlueData(blueFileData);
        setRedPoints(redFileData.length);
        setBluePoints(blueFileData.length);
      };
      reader.readAsText(file);
    } else if (file.name.endsWith(".xlsx")) {
      try {
        const rows = await readXlsxFile(file);
        const redFileData: Point[] = [];
        const blueFileData: Point[] = [];
        rows.slice(1).forEach(([x, y, type]) => {
          const point = {
            x: parseFloat(x as string),
            y: parseFloat(y as string),
          };
          if ((type as string)?.trim().toLowerCase() === "red") {
            redFileData.push(point);
          } else if ((type as string)?.trim().toLowerCase() === "blue") {
            blueFileData.push(point);
          }
        });
        setRedData(redFileData);
        setBlueData(blueFileData);
        setRedPoints(redFileData.length);
        setBluePoints(blueFileData.length);
      } catch (error) {
        console.error("Error reading .xlsx file:", error);
      }
    }
  };

  return (
    <div className={classes.outerDiv}>
      <Typography variant="h3" className={classes.title} marginBottom={2}>
        Ham Sandwich Cut 🥪
      </Typography>


      {/* Hide everything except step navigation when Teach Mode is ON */}
      <Collapse in={!teachMode}>
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          gap={1}
          flexDirection="row"
          width="100%"
          height={"120px"}
          marginTop={0}
        >
          <TextField
            label="Number of Red Points"
            type="number"
            value={redPoints}
            onChange={(e) =>
              setRedPoints(Math.min(Math.max(1, Number(e.target.value)), 10000))
            }
          />
          <TextField
            label="Number of Blue Points"
            type="number"
            value={bluePoints}
            onChange={(e) =>
              setBluePoints(
                Math.min(Math.max(1, Number(e.target.value)), 10000)
              )
            }
          />
          <Button
            variant="contained"
            onClick={() => {
              randomiseData();
              if (teachMode) {
                setCurrentStepIndex(0);
              }
            }}
            sx={{ height: "36.5px" }}
          >
            Randomise Chart
          </Button>

          {/* File Upload & Download Button */}
          <FileUploadDownloadButton handleFileUpload={handleFileUpload} />
        </Box>
      </Collapse>

      {/* Fixed Step Navigation Container */}
      <Collapse in={teachMode}>
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          flexDirection="column"
          minWidth="300px"
          height="120px"
          overflow="hidden"
        >
          {teachMode &&
            stepsTaken.length > 0 &&
            !hasError &&
            !isCalculating && (
              <Box
                display="flex"
                flexDirection="column"
                alignItems="center"
                gap={2}
              >
                <Typography
                  variant="h5"
                  sx={{
                    whiteSpace: "nowrap",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    maxWidth: "100%",
                    typography: { sm: "body1", xs: "body2" },
                  }}
                >
                  Step {currentStepIndex + 1}:{" "}
                  {stepsTaken[currentStepIndex]?.description}
                  {currentStepData?.oddIntersectionProperty
                    ? ` Odd number of intersections.`
                    : ""}
                </Typography>

                <Box display="flex" gap={2}>
                  <Tooltip title="Previous Step">
                    <span>
                      <Button
                        variant="outlined"
                        onClick={() =>
                          setCurrentStepIndex((prev) => Math.max(prev - 1, 0))
                        }
                        disabled={currentStepIndex === 0}
                      >
                        <ArrowBack />
                      </Button>
                    </span>
                  </Tooltip>

                  <Tooltip title="Next Step">
                    <span>
                      <Button
                        variant="outlined"
                        onClick={() =>
                          setCurrentStepIndex((prev) =>
                            Math.min(prev + 1, stepsTaken.length - 1)
                          )
                        }
                        disabled={currentStepIndex === stepsTaken.length - 1}
                      >
                        <ArrowForward />
                      </Button>
                    </span>
                  </Tooltip>
                </Box>
              </Box>
            )}
        </Box>
      </Collapse>

      {/* Graph with Overlay for Calculating/Error Message */}
      <div className={classes.outerGraphDiv}>
        <div className={classes.innerGraphDiv}>
          {/* Teach Mode Button - Positioned Top Right */}
          <Box
            sx={{
              position: "absolute",
              top: 10,
              right: 10,
              zIndex: 20, // Higher than overlay (which is z-index: 10)
              backgroundColor: "rgba(255, 255, 255, 0.8)", // Light background for visibility
              borderRadius: "50%",
              padding: "6px",
              boxShadow: 3, // Subtle shadow
              cursor: "pointer",
            }}
          >
            <Tooltip title="Toggle Teach Mode">
              <IconButton
                onClick={() => setTeachMode(!teachMode)}
                color={teachMode ? "primary" : "default"}
              >
                <MenuBook />
              </IconButton>
            </Tooltip>
          </Box>

          <Line data={chartData} options={options} />

          {/* Overlay for Calculating/Error Message */}
          {(isCalculating || hasError) && (
            <div className={classes.overlay}>
              <Typography
                variant="h4"
                color={hasError ? "error" : "textSecondary"}
                sx={{ typography: { sm: "h4", xs: "h5" } }}
              >
                {isCalculating ? (
                  <>
                    Calculating
                    <Box
                      className={classes.dots}
                      sx={{ display: "inline-flex", gap: "2px" }}
                    >
                      <span className={classes.dot}>.</span>
                      <span className={classes.dot}>.</span>
                      <span className={classes.dot}>.</span>
                    </Box>
                  </>
                ) : (
                  "⚠️ Something went wrong. Please try again."
                )}
              </Typography>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ReactChartJs;
