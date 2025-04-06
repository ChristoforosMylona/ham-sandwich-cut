import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import DownloadIcon from "@mui/icons-material/Download";
import { Button, ButtonGroup, Menu, MenuItem } from "@mui/material";
import React, { ChangeEvent, MouseEvent, useState } from "react";
import { downloadFile } from "../api/api";

interface FileUploadDownloadButtonProps {
  handleFileUpload: (e: ChangeEvent<HTMLInputElement>) => void;
  handleDownloadCurrentPointSet: () => void; // Function to download the current point set
}

const FileUploadDownloadButton: React.FC<FileUploadDownloadButtonProps> = ({
  handleFileUpload,
  handleDownloadCurrentPointSet,
}) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  // Open dropdown menu
  const handleClick = (event: MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };

  // Close dropdown menu
  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleDownloadSample = async (fileType: "csv" | "json" | "excel") => {
    handleClose(); // Close dropdown after selection
    try {
      await downloadFile(fileType);
    } catch (error) {
      console.error("Error downloading file:", error);
    }
  };

  return (
    <div>
      {/* Button Group for Upload and Download */}
      <ButtonGroup variant="contained" sx={{ display: "flex", alignItems: "stretch" }}>
        {/* Upload Button */}
        <Button
          startIcon={<CloudUploadIcon />}
          component="label"
          sx={{
            color: "text.primary",
            backgroundColor: "primary.main",
            "&:hover": {
              backgroundColor: "primary.dark",
            },
          }}
        >
          Upload
          {/* Hidden file input for uploading files */}
          <input
            type="file"
            hidden
            accept=".json,.csv,.xlsx"
            onChange={handleFileUpload}
          />
        </Button>

        {/* Download Button with Dropdown Icon */}
        <Button
          endIcon={<ArrowDropDownIcon />}
          onClick={handleClick} // Opens dropdown for download options
          sx={{
            color: "text.primary",
            backgroundColor: "primary.main",
            paddingLeft: "0", // Remove extra padding to the left of the icon
            "&:hover": {
              backgroundColor: "primary.dark",
            },
          }}
        />
      </ButtonGroup>

      {/* Dropdown Menu for Download Options */}
      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleClose}>
        <MenuItem onClick={() => handleDownloadSample("csv")}>
          Download Sample CSV
        </MenuItem>
        <MenuItem onClick={() => handleDownloadSample("json")}>
          Download Sample JSON
        </MenuItem>
        <MenuItem onClick={() => handleDownloadSample("excel")}>
          Download Sample Excel
        </MenuItem>
        <MenuItem
          onClick={() => {
            handleClose();
            handleDownloadCurrentPointSet(); // Call the function to download the current point set
          }}
        >
          <DownloadIcon sx={{ marginRight: 1 }} />
          Download Current Point Set
        </MenuItem>
      </Menu>
    </div>
  );
};

export default FileUploadDownloadButton;