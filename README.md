# Inscopix Data Processing Software & Python API Installation Guide

This document describes how to install the core Inscopix Data Processing Software on Linux and set up the Python API in editable (pip) mode.

---

## System Requirements

- **Operating Systems (64-bit)**  
  - Linux: CentOS 7, Ubuntu 18.04–20.04  
- **Hardware**  
  - RAM: 32 GB (≥ 64 GB recommended for CNMF)  
  - Storage: 1 TB SSD  
  - CPU: 3.0 GHz, 4–8 cores  
  - Display: 1920 × 1080  
- **Python**  
  - Version 3.7–3.9

---

## 1. Core Software Installation (Linux)

1. **Download** the Linux installer (`Inscopix Data Processing 1.x.x.sh`) from your Inscopix support portal.  
2. **Place** the `.sh` file in the directory where you want the software installed.  
3. **Ensure** the following tools are on your `PATH`:
   ```bash
   which tar gunzip tail


These are required by the self-extracting stub.
4\. **Run** the installer stub:

```bash
bash Inscopix\ Data\ Processing\ 1.x.x.sh
```

This unpacks two folders under your current directory:

* `Inscopix Data Processing/` (wrapper script)
* `Inscopix Data Processing.linux/` (binaries, libraries, resources)

5. **Launch** the GUI application:

   ```bash
   cd "Inscopix Data Processing 1.x.x"
   ./Inscopix\ Data\ Processing
   ```
6. **Activation**
   When prompted, enter your activation ID. Contact support at [support.inscopix@bruker.com](mailto:support.inscopix@bruker.com) for assistance.

---

## 2. Python API Installation (pip)

1. **Change** into the API folder:

   ```bash
   cd <install_dir>/Inscopix\ Data\ Processing.linux/Contents/API/Python
   ```
2. **Install** the API in editable mode:

   ```bash
   pip install -e .
   ```
3. **Verify** the installation:

   ```bash
   python3 -c "import isx"
   ```

   If no errors occur, the API is installed correctly.

---