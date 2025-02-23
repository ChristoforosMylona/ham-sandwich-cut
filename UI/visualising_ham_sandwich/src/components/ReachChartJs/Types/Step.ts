import { ChartDataset } from "chart.js";

// Define the types for points and other data structures
export type Point = {
    x: number;
    y: number;
    color?: 'red' | 'blue'; // Optional color for interval median points
};

export type DualLine = {
    m: number; // slope
    b: number; // intercept
};

export type Interval = {
    start: number;
    end: number;
};

export type Cut = {
    slope: number;
    intercept: number;
};

// Define the possible step data types
export interface StepData {
    dualLines?: {
        red: DualLine[];
        blue: DualLine[];
    };
    intervalMedians?: Point[];
    interval?: Interval;
    cut?: Cut;
    chosenSide?: 'left' | 'right';
    oddIntersectionProperty?: boolean;
}

// Define the structure for each step
export interface Step {
    id: number;
    type: 'dual_lines_calculation' | 'interval_check' | 'iteration_step' | 'compute_cut';
    description: string;
    data: StepData;
}


// Define the type of datasets that we will be working with
export interface ScatterChartDataset extends ChartDataset<'scatter', Point> {
    borderWidth?: number;
  }