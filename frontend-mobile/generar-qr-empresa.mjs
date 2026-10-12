import QRCode from "qrcode";
import { fileURLToPath, URL } from "node:url";

await QRCode.toFile(fileURLToPath(new URL("./public/qr-empresa.png", import.meta.url)), "TRUKLY:EMPRESA:PRINCIPAL", {
  width: 1200,
  margin: 4,
  errorCorrectionLevel: "H",
});
