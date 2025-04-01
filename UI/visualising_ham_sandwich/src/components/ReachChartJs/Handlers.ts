import React, { Dispatch, SetStateAction } from "react";

// // Function to handle algorithm selection
// export const handleAlgorithmChange = (
//   e: React.ChangeEvent<{ value: unknown }>,
//   setSelectedEndpoint: Dispatch<SetStateAction<string>>,
//   redPoints: number,
//   setRedPoints: Dispatch<SetStateAction<number>>,
//   bluePoints: number,
//   setBluePoints: Dispatch<SetStateAction<number>>,
//   setRedWarning: Dispatch<SetStateAction<boolean>>,
//   setBlueWarning: Dispatch<SetStateAction<boolean>>
// ) => {
//   const newAlgorithm = e.target.value as string;
//   setSelectedEndpoint(newAlgorithm);

//   if (newAlgorithm !== "default") {
//     if (redPoints > 50) {
//       setRedPoints(50);
//       setRedWarning(true);
//     } else {
//       setRedWarning(false);
//     }

//     if (bluePoints > 50) {
//       setBluePoints(50);
//       setBlueWarning(true);
//     } else {
//       setBlueWarning(false);
//     }
//   } else {
//     setRedWarning(false);
//     setBlueWarning(false);
//   }
// };

export const handlePointsChange = (
  e: React.ChangeEvent<HTMLInputElement>,
  selectedEndpoint: string,
  setPoints: Dispatch<SetStateAction<number>>,
  setWarning: Dispatch<SetStateAction<boolean>>
) => {
  // const maxPoints = selectedEndpoint != "ham-sandwich-mlp" ? 1000 : 50;
  const maxPoints = 50;
  const value = Math.min(Math.max(1, Number(e.target.value)), maxPoints);

  setPoints(value);
  setWarning(selectedEndpoint === "ham-sandwich-mlp" && value > 50);
}