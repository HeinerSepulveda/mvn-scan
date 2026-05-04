# Maven Component Scanner

Vulnerability scanner for Maven components using the OSS Index (Sonatype) API.

---

## 🚀 Description

**mvn-scan** is a command-line interface (CLI) tool designed to analyze Maven project dependencies and detect known vulnerabilities (CVEs) using the OSS Index API by Sonatype.

It is built to help identify security risks in both direct and transitive dependencies, generating clear and detailed HTML reports.

---

## 🔍 Features

* Dependency analysis from:

  * `.txt` files
  * `.xml` files (`pom.xml`)
  * `.war` files
* Vulnerability detection (CVEs)
* Identification of direct and transitive dependencies
* HTML report generation
* Integration with OSS Index (Sonatype)
* Persistent API token configuration

---

## 📦 Installation

```bash
pip install mvn-scan
```

---

## ⚙️ Usage

```bash
mvn-scan -txt <file.txt> [-out <output.html>]
mvn-scan -xml <file.xml> [-out <output.html>]
mvn-scan -war <file.war> [-out <output.html>]
```

---

## 🔑 API Key Configuration

This tool requires an API Key from OSS Index (Sonatype).

### Save API Key (recommended)

```bash
mvn-scan --set-api-token YOUR_API_KEY
```

This will store the configuration in:

```
~/.mvnScan/config.json
```

---

### Use with API Key directly

```bash
mvn-scan -txt deps.txt --api-key YOUR_API_KEY
```

---

## 🧪 Examples

```bash
mvn-scan -txt deps.txt

mvn-scan -xml pom.xml -out report.html

mvn-scan -war file.war --api-key YOUR_API_KEY
```

---

## 📄 Report

The scanner generates an HTML report that includes:

* Detected vulnerabilities
* Associated CVEs
* Severity level
* Affected components
* Direct and transitive dependencies

---

## 🛠️ Requirements

* Python >= 3.8
* OSS Index API Key (required)

---

## 🌐 API Used

This project uses the OSS Index (Sonatype) API to query component vulnerabilities.

More information:
https://ossindex.sonatype.org/

---

## 👨‍💻 Author

**Edwin Geinner Castro Sepulveda**

GitHub:
https://github.com/HeinerSepulveda

---

## 📜 License

This project is licensed under the MIT License.

See the LICENSE file for more details.
