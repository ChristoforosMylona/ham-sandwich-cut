import { Dispatch, SetStateAction } from "react";

// Function to handle algorithm selection
export const handleAlgorithmChange = (
  e: React.ChangeEvent<{ value: unknown }>,
  setSelectedEndpoint: Dispatch<SetStateAction<string>>,
  redPoints: number,
  setRedPoints: Dispatch<SetStateAction<number>>,
  bluePoints: number,
  setBluePoints: Dispatch<SetStateAction<number>>,
  setRedWarning: Dispatch<SetStateAction<boolean>>,
  setBlueWarning: Dispatch<SetStateAction<boolean>>
) => {
  const newAlgorithm = e.target.value as string;
  setSelectedEndpoint(newAlgorithm);

  if (newAlgorithm !== "default") {
    if (redPoints > 50) {
      setRedPoints(50);
      setRedWarning(true);
    } else {
      setRedWarning(false);
    }

    if (bluePoints > 50) {
      setBluePoints(50);
      setBlueWarning(true);
    } else {
      setBlueWarning(false);
    }
  } else {
    setRedWarning(false);
    setBlueWarning(false);
  }
};

// Function to handle red points change
export const handleRedPointsChange = (
  e: React.ChangeEvent<HTMLInputElement>,
  selectedEndpoint: string,
  setRedPoints: Dispatch<SetStateAction<number>>,
  setRedWarning: Dispatch<SetStateAction<boolean>>
) => {
  const maxPoints = selectedEndpoint !== "default" ? 50 : 10000;
  const value = Math.min(Math.max(1, Number(e.target.value)), maxPoints);

  setRedPoints(value);
  setRedWarning(selectedEndpoint !== "default" && value > 50);
};

// Function to handle blue points change
export const handleBluePointsChange = (
  e: React.ChangeEvent<HTMLInputElement>,
  selectedEndpoint: string,
  setBluePoints: Dispatch<SetStateAction<number>>,
  setBlueWarning: Dispatch<SetStateAction<boolean>>
) => {
  const maxPoints = selectedEndpoint !== "default" ? 50 : 10000;
  const value = Math.min(Math.max(1, Number(e.target.value)), maxPoints);

  setBluePoints(value);
  setBlueWarning(selectedEndpoint !== "default" && value > 50);
};
