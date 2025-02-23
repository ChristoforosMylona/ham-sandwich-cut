import React from "react";
import { Button } from "@mui/material";

interface FileUploadButtonProps {
  handleFileUpload: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

const FileUploadButton: React.FC<FileUploadButtonProps> = ({ handleFileUpload }) => {
  return (
    <Button
      variant="contained"
      component="label"
      sx={{
        color: "text.primary",
        backgroundColor: "primary.main",
        '&:hover': {
          backgroundColor: "primary.dark",
        },
      }}
    >
      Upload File
      {/* Hidden file input */}
      <input
        type="file"
        hidden
        accept=".json,.csv,.xlsx"
        onChange={handleFileUpload}
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          opacity: 0,
          cursor: "pointer",
        }}
      />
    </Button>
  );
};

export default FileUploadButton;
