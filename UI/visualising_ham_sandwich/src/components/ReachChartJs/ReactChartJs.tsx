import {
  ArrowBack,
  ArrowForward,
  FirstPage,
  HelpOutline,
  LastPage,
  MenuBook,
  ZoomOutMap,
} from "@mui/icons-material";
import {
  Box,
  Button,
  Collapse,
  FormHelperText,
  IconButton,
  TextField,
  Tooltip,
  Typography,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import {
  CategoryScale,
  ChartData,
  ChartDataset,
  Chart as ChartJS,
  ChartOptions,
  LinearScale,
  LineElement,
  PointElement,
  registerables,
  Tooltip as TooltipJS,
} from "chart.js";
import annotationPlugin from "chartjs-plugin-annotation";
import "chartjs-plugin-dragdata";
import zoomPlugin from "chartjs-plugin-zoom";
import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { Line } from "react-chartjs-2";
import readXlsxFile from "read-excel-file";
import { calculateLine } from "../api/CalculateLineService";
import { hamSandwichLineTooltipPlugin } from "../Plugins/hamSandwichLineTooltipPlugin";
import FileUploadDownloadButton from "./FileUploadDownloadButton";
import { handlePointsChange } from "./Handlers";
import { Point, Step, StepData } from "./Types/Step";

import classes from "./ReactChartJs.module.scss";
import { isVerticalCut } from "../Util/isVerticalCut";

ChartJS.register(...registerables, annotationPlugin, zoomPlugin);
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  TooltipJS,
  hamSandwichLineTooltipPlugin
);
const PADDING_FACTOR = 2;

const ReactChartJs: React.FC = () => {
  const isMobile = useMediaQuery("(max-width:750px)");

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

  const chartRef = useRef<ChartJS<"line", number[], string>>(null);

  const [isCalculating, setIsCalculating] = useState(false);

  const [hasError, setHasError] = useState(false);
  // State for Teach Mode Steps
  const [stepsTaken, setStepsTaken] = useState<Step[]>([]);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [finalCut, setFinalCut] = useState<{
    slope: number | null;
    intercept: number | null;
    x_intercept: number | null; // For vertical lines
    is_vertical: boolean;
  } | null>(null);

  const [currentStepData, setCurrentStepData] = useState<StepData | null>(null);

  // State for Teach Mode
  const [teachMode, setTeachMode] = useState(false);

  // state for selected endpoint
  const [selectedEndpoint, setSelectedEndpoint] = useState("default");
  const [redWarning, setRedWarning] = useState<boolean>(false);
  const [blueWarning, setBlueWarning] = useState<boolean>(false);

  const theme = useTheme();

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
      teachMode,
      selectedEndpoint
    );
  }, [
    redData,
    blueData,
    teachMode,
    setIsCalculating,
    setHasError,
    setStepsTaken,
    setFinalCut,
    selectedEndpoint,
  ]);

  const chartDataSets = useMemo<ChartData<"line">>(() => {
    const datasets: ChartDataset<"line">[] = [];

    if (
      (teachMode &&
        !(currentStepIndex > 1 && currentStepIndex != stepsTaken.length - 1)) ||
      !teachMode
    ) {
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
    }

    // Add line dataset if finalCut exists
    if (finalCut) {
      const xRange = graphBounds.maxX - graphBounds.minX;
      const paddedMinX = graphBounds.minX - xRange * PADDING_FACTOR;
      const paddedMaxX = graphBounds.maxX + xRange * PADDING_FACTOR;

      let lineData: Point[] = [];

      // Check for vertical line
      if (finalCut.is_vertical) {
        // For vertical lines, use x_intercept (ensure it's a number)
        const xIntercept = finalCut.x_intercept;

        if (xIntercept !== null) {
          lineData = [
            { x: xIntercept, y: graphBounds.minY }, // Start from the bottom of the graph
            { x: xIntercept, y: graphBounds.maxY }, // End at the top of the graph
          ];
        }
      } else if (finalCut.slope !== null && finalCut.intercept !== null) {
        // For non-vertical lines, calculate y-values using slope and intercept
        const slope = finalCut.slope;
        const intercept = finalCut.intercept;

        lineData = [
          {
            x: paddedMinX,
            y: slope * paddedMinX + intercept,
          },
          {
            x: paddedMaxX,
            y: slope * paddedMaxX + intercept,
          },
        ];
      }

      datasets.push({
        label: "Ham Sandwich Cut",
        data: lineData,
        borderColor: "rgba(75, 192, 192, 1)",
        borderWidth: 2,
        showLine: true,
        fill: false,
        pointRadius: 0, // No visible points
        pointHitRadius: 20, // Makes the line itself hoverable for tooltips
        backgroundColor: "rgba(75, 192, 192, 1)",
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
      if (currentStepIndex >= 1) {
        const duals = stepsTaken[1].data.dualLines;

        ["red", "blue"].forEach((color) => {
          const dualLines = duals?.[color as "red" | "blue"];
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
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      dragData: {
        round: 3,
        dragX: true,
        dragY: true,
        showTooltip: true,
        onDragStart: function (
          e: TouchEvent | MouseEvent,
          _datasetIndex: number,
          _index: number,
          _value: any
        ): boolean {
          // Desktop: allow drag if mouse is down on a point
          if (!("touches" in e)) {
            return true;
          }

          // Mobile: use the original TouchEvent for hit testing
          const chart = chartRef.current;
          if (!chart) return false;

          // Use the original event for hit testing
          const elements = chart.getElementsAtEventForMode(
            e, // Pass the original TouchEvent
            "nearest",
            { intersect: true },
            false
          );

          if (elements && elements.length > 0) {
            // Disable pan while dragging
            if (chart.options.plugins?.zoom?.pan) {
              chart.options.plugins.zoom.pan.enabled = false;
            }
            return true;
          }

          // Not touching a point: allow pan
          if (chart.options.plugins?.zoom?.pan) {
            chart.options.plugins.zoom.pan.enabled = true;
          }
          return false;
        },
        onDragEnd: function (
          _e: TouchEvent | MouseEvent,
          _datasetIndex: number,
          _index: number,
          _value: any
        ) {
          // Re-enable panning after drag
          const chart = chartRef.current;
          if (chart?.options.plugins?.zoom?.pan) {
            chart.options.plugins.zoom.pan.enabled = true;
          }
          memoizedCalculateLine();
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
          overScaleMode: "xy",
        },
        pan: {
          enabled: true,
          mode: "xy",
          modifierKey: "ctrl",
          threshold: 15,
        },
      },
      tooltip: {
        displayColors: false,
        enabled: true, // Ensure tooltips are enabled
        external: function (context) {
          const { chart, tooltip } = context;
          let tooltipEl = document.getElementById("chartjs-custom-tooltip");
          if (!tooltipEl) {
            tooltipEl = document.createElement("div");
            tooltipEl.id = "chartjs-custom-tooltip";
            tooltipEl.style.position = "absolute";
            tooltipEl.style.pointerEvents = "none";
            tooltipEl.style.background = "rgba(0,0,0,0.8)";
            tooltipEl.style.color = "white";
            tooltipEl.style.borderRadius = "4px";
            tooltipEl.style.padding = "6px 8px";
            tooltipEl.style.fontSize = "14px";
            tooltipEl.style.zIndex = "1000";
            document.body.appendChild(tooltipEl);
          }

          // Always hide if tooltip is not visible
          if (tooltip.opacity === 0) {
            tooltipEl.style.opacity = "0";
            return;
          }

          const isHamSandwich =
            tooltip.dataPoints?.[0]?.dataset.label === "Ham Sandwich Cut";
          if (isHamSandwich) {
            tooltip.options.enabled = false;
            tooltipEl.innerHTML = tooltip.body?.[0]?.lines?.[0] ?? "";
            const mouse = (chart as any)._hamSandwichTooltipMouse;
            if (mouse) {
              const canvasRect = chart.canvas.getBoundingClientRect();
              tooltipEl.style.opacity = "1";
              tooltipEl.style.left =
                canvasRect.left + window.scrollX + mouse.x + 10 + "px";
              tooltipEl.style.top =
                canvasRect.top + window.scrollY + mouse.y + 10 + "px";
            } else {
              tooltipEl.style.opacity = "0";
            }
          } else {
            tooltip.options.enabled = true;
            tooltipEl.style.opacity = "0";
          }
        },
        callbacks: {
          label: function (context) {
            // Show equation if this is the Ham Sandwich Cut line and the mouse is not on a real point
            if (
              context.dataset.label === "Ham Sandwich Cut" &&
              (context.dataIndex === 0 || context.dataIndex === 1)
            ) {
              const cut = currentStepData?.cut || finalCut;
              if (cut) {
                if (
                  isVerticalCut(cut) &&
                  cut.is_vertical &&
                  cut.x_intercept !== null
                ) {
                  return `Ham Sandwich Cut: x = ${cut.x_intercept.toFixed(2)}`;
                } else if (cut.slope !== null && cut.intercept !== null) {
                  return `Ham Sandwich Cut: y = ${cut.slope.toFixed(
                    2
                  )}x + ${cut.intercept.toFixed(2)}`;
                }
              }
            }
            // Default: show normal point info
            const raw = context.raw as { x: number; y: number };
            if (context.dataset.label === "Ham Sandwich Cut Dual Point") {
              return `Dual Point: (${raw.x.toFixed(2)}, ${raw.y.toFixed(2)})`;
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

  useEffect(() => {
    return () => {
      const tooltipEl = document.getElementById("chartjs-custom-tooltip");
      if (tooltipEl) tooltipEl.remove();
    };
  }, []);

  const handleDownloadCurrentPointSet = () => {
    // Create an object containing the current red and blue points
    const currentPointSet = {
      redPoints: redData, // Array of red points
      bluePoints: blueData, // Array of blue points
    };

    // Convert the object to a JSON string
    const jsonString = JSON.stringify(currentPointSet, null, 2);

    // Create a Blob from the JSON string
    const blob = new Blob([jsonString], { type: "application/json" });

    // Create a URL for the Blob
    const url = URL.createObjectURL(blob);

    // Create a temporary anchor element to trigger the download
    const link = document.createElement("a");
    link.href = url;
    link.download = "current_point_set.json"; // File name for the downloaded file
    link.click();

    // Revoke the Blob URL to free up memory
    URL.revokeObjectURL(url);
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

  useEffect(() => {
    memoizedCalculateLine();
  }, [redData, blueData, selectedEndpoint]);

  // Memoized handlers
  const memoizedAlgorithmChange = useCallback(
    (e: React.ChangeEvent<{ value: unknown }>) =>
      setSelectedEndpoint(e.target.value as string),
    [setSelectedEndpoint]
  );

  const memoizedRedPointsChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) =>
      handlePointsChange(e, selectedEndpoint, setRedPoints, setRedWarning),
    [selectedEndpoint]
  );

  const memoizedBluePointsChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) =>
      handlePointsChange(e, selectedEndpoint, setBluePoints, setBlueWarning),
    [selectedEndpoint]
  );

  useEffect(() => {
    if (selectedEndpoint === "ham-sandwich-mlp") {
      if (redPoints > 50) {
        setRedPoints(50);
        setRedWarning(true);
      }
      if (bluePoints > 50) {
        setBluePoints(50);
        setBlueWarning(true);
      }
    } else {
      setBlueWarning(false);
      setRedWarning(false);
    }
  }, [
    selectedEndpoint,
    setRedPoints,
    setBluePoints,
    bluePoints,
    redPoints,
    setRedWarning,
    setBlueWarning,
  ]);

  return (
    <div className={classes.outerDiv}>
      <Box
        display="flex"
        flexDirection={{ xs: "column", custom1050: "row" }}
        alignItems="center"
        width="100%"
        marginBottom={{ xs: 4, custom1050: 2 }}
        gap={2}
      >
        {/* Title */}
        <Typography
          variant="h3"
          className={classes.title}
          sx={{
            fontSize: { xs: "1.75rem", sm: "2.5rem", custom1050: "3rem" },
            mb: { xs: 2, custom1050: 0 },
            textAlign: "center",
            width: "100%",
            order: { xs: 1, custom1050: 2 },
          }}
        >
          Ham Sandwich Cut
          <Box
            component="span"
            sx={{
              display: { xs: "none", custom350: "inline" },
            }}
          >
            {" 🥪"}
          </Box>
        </Typography>

        {/* Endpoint Selection */}
        <Box
          sx={{
            width: { xs: "100%", sm: "300px" },
            display: "flex",
            justifyContent: "center",
            position: { xs: "static", custom1050: "absolute" },
            left: { custom1050: 20 },
            order: { xs: 2, custom1050: 1 },
          }}
        >
          <TextField
            select
            label="Choose Algorithm"
            value={selectedEndpoint}
            onChange={(e) => {
              if (e.target.value !== "default") {
                setTeachMode(false);
              }
              memoizedAlgorithmChange(e);
              setSelectedEndpoint(e.target.value);
            }}
            SelectProps={{ native: true }}
            variant="outlined"
            sx={{
              width: "100%",
              "& .MuiInputLabel-root": {
                position: "relative",
                transform: "none",
                marginBottom: 1,
              },
              "& .MuiSelect-select": {
                paddingTop: 2,
              },
            }}
          >
            <option value="default">Simplified L-M-S Algorithm</option>
            <option value="brute-force">Brute Force</option>
            <option value="ham-sandwich-mlp">MILP Method</option>
          </TextField>
        </Box>
      </Box>

      {/* Hide everything except step navigation when Teach Mode is ON */}
      <Collapse in={!teachMode}>
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          gap={1}
          flexDirection={{ xs: "column", sm: "row" }} // Stack vertically on mobile
          width="100%"
          height={{ xs: "auto", sm: "120px" }} // Auto height on mobile
          marginTop={0}
          padding={1}
        >
          {/* Points inputs in a row on mobile */}
          {/* <Box
            display="flex"
            flexDirection={{ xs: "column", sm: "row" }}
            gap={1}
            width="100%"
          > */}
          {/* Red Points Input with Fixed Helper Text */}
          <Tooltip title="Max 50 points per set due to limited hardware">
            <Box position="relative" width={{ xs: "100%", sm: 150 }}>
              <TextField
                label="Number of Red Points"
                type="number"
                value={redPoints}
                onChange={memoizedRedPointsChange}
                error={redWarning}
                inputProps={{
                  min: 1,
                  // max: selectedEndpoint != "ham-sandwich-mlp" ? 1000 : 50,
                  max: 50,
                }}
                sx={{ width: "100%" }}
              />
              {redWarning && (
                <FormHelperText
                  error
                  sx={{ position: "absolute", bottom: -20 }}
                >
                  ⚠️ Max 50 points
                </FormHelperText>
              )}
            </Box>
          </Tooltip>

          <Tooltip title="Max 50 points per set due to limited hardware">
            {/* Blue Points Input with Fixed Helper Text */}
            <Box position="relative" width={{ xs: "100%", sm: 150 }}>
              <TextField
                label="Number of Blue Points"
                type="number"
                value={bluePoints}
                onChange={memoizedBluePointsChange}
                error={blueWarning}
                inputProps={{
                  min: 1,
                  // max: selectedEndpoint != "ham-sandwich-mlp" ? 1000 : 50,
                  max: 50,
                }}
                sx={{ width: "100%" }}
              />
              {blueWarning && (
                <FormHelperText
                  error
                  sx={{ position: "absolute", bottom: -20 }}
                >
                  ⚠️ Max 50 points
                </FormHelperText>
              )}
            </Box>
          </Tooltip>
          {/* </Box> */}

          {/* Randomize Button */}
          <Box
            display="flex"
            flexDirection={{ xs: "row", sm: "row" }}
            gap={1}
            width={{ xs: "100%", sm: "auto" }}
            justifyContent="center"
          >
            <Button
              variant="contained"
              onClick={() => {
                if (teachMode) {
                  setCurrentStepIndex(0);
                }
                setFinalCut(null);
                randomiseData();
              }}
              sx={{
                height: "36.5px",
                flex: { xs: 1, sm: "none" },
              }}
            >
              Randomise
            </Button>

            {/* File Upload & Download */}
            <Box sx={{ flex: { xs: 1, sm: "none" } }}>
              <FileUploadDownloadButton
                handleFileUpload={handleFileUpload}
                handleDownloadCurrentPointSet={handleDownloadCurrentPointSet}
              />
            </Box>
          </Box>
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
                  {/* First Step */}
                  <Tooltip title="First Step">
                    <span>
                      <Button
                        variant="outlined"
                        onClick={() => setCurrentStepIndex(0)}
                        disabled={currentStepIndex === 0}
                      >
                        <FirstPage />
                      </Button>
                    </span>
                  </Tooltip>

                  {/* Previous Step */}
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

                  {/* Next Step */}
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

                  {/* Last Step */}
                  <Tooltip title="Last Step">
                    <span>
                      <Button
                        variant="outlined"
                        onClick={() =>
                          setCurrentStepIndex(stepsTaken.length - 1)
                        }
                        disabled={currentStepIndex === stepsTaken.length - 1}
                      >
                        <LastPage />
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
          {selectedEndpoint === "default" && (
            <Box
              sx={{
                position: "absolute",
                top: 10,
                right: 10,
                zIndex: 20,
                backgroundColor:
                  theme.palette.mode === "dark"
                    ? "rgba(255, 255, 255, 0.2)"
                    : "rgba(0, 0, 0, 0.1)",
                borderRadius: "50%",
                padding: "6px",
                boxShadow: 3,
                cursor: "pointer",
                opacity: 0.5,
                transition:
                  "opacity 0.3s ease-in-out, background-color 0.3s ease-in-out",
                "&:hover": {
                  opacity: 1,
                  backgroundColor:
                    theme.palette.mode === "dark"
                      ? "rgba(255, 255, 255, 0.4)"
                      : "rgba(0, 0, 0, 0.2)",
                },
              }}
              className={classes.teachModeButton}
            >
              <Tooltip title="Toggle Teach Mode">
                <IconButton
                  className={classes.teachModeButton}
                  onClick={() => {
                    if (!teachMode) {
                      setFinalCut(null);
                    }
                    setTeachMode(!teachMode);
                  }}
                  color={teachMode ? "primary" : "default"}
                >
                  <MenuBook />
                </IconButton>
              </Tooltip>
            </Box>
          )}

          {/* Chart */}
          <Line data={chartData} options={options} ref={chartRef} />

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
                  <>
                    ⚠️ Something went wrong. Please try again.
                    {selectedEndpoint === "default" && (
                      <Typography
                        variant="body1"
                        sx={{
                          marginTop: 2,
                          fontSize: "body1",
                          fontStyle: "italic",
                        }}
                      ></Typography>
                    )}
                  </>
                )}
              </Typography>
            </div>
          )}

          {/* Reset Zoom Button - Positioned Left of Help Icon */}
          <Box
            sx={{
              position: "absolute",
              bottom: 10,
              right: isMobile ? 10 : 75, // Move to right edge if help icon is hidden
              zIndex: 20,
              backgroundColor:
                theme.palette.mode === "dark"
                  ? "rgba(255, 255, 255, 0.2)"
                  : "rgba(0, 0, 0, 0.1)",
              borderRadius: "50%",
              padding: "6px",
              boxShadow: 3,
              cursor: "pointer",
              opacity: 0.5,
              transition:
                "opacity 0.3s ease-in-out, background-color 0.3s ease-in-out",
              "&:hover": {
                opacity: 1,
                backgroundColor:
                  theme.palette.mode === "dark"
                    ? "rgba(255, 255, 255, 0.4)"
                    : "rgba(0, 0, 0, 0.2)",
              },
            }}
          >
            <Tooltip title="Reset zoom & pan">
              <IconButton
                color="default"
                onClick={() => chartRef.current?.resetZoom()}
              >
                <ZoomOutMap />
              </IconButton>
            </Tooltip>
          </Box>

          {/* Pan & Zoom Help Icon - Positioned Bottom Right */}
          {!isMobile && (
            <Box
              sx={{
                position: "absolute",
                bottom: 10,
                right: 10,
                zIndex: 20,
                backgroundColor:
                  theme.palette.mode === "dark"
                    ? "rgba(255, 255, 255, 0.2)"
                    : "rgba(0, 0, 0, 0.1)",
                borderRadius: "50%",
                padding: "6px",
                boxShadow: 3,
                cursor: "pointer",
                opacity: 0.5,
                transition:
                  "opacity 0.3s ease-in-out, background-color 0.3s ease-in-out",
                "&:hover": {
                  opacity: 1,
                  backgroundColor:
                    theme.palette.mode === "dark"
                      ? "rgba(255, 255, 255, 0.4)"
                      : "rgba(0, 0, 0, 0.2)",
                },
              }}
            >
              <Tooltip title="Hold Ctrl to Pan & Zoom">
                <IconButton color="default">
                  <HelpOutline />
                </IconButton>
              </Tooltip>
            </Box>
          )}
        </div>
      </div>
    </div>
  );
};

export default ReactChartJs;
