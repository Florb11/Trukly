import avatarPredeterminado from "../assets/avatar-predeterminado.png";

export default function FotoPerfil({ src, alt = "Foto de perfil" }) {
  return <img key={src || "predeterminado"} src={src || avatarPredeterminado} alt={alt}
    style={{ width: "100%", height: "100%", objectFit: "cover", display: "block", borderRadius: "inherit" }}
    onError={(event) => {
      if (event.currentTarget.dataset.avatarPredeterminado) return;
      event.currentTarget.dataset.avatarPredeterminado = "true";
      event.currentTarget.src = avatarPredeterminado;
    }} />;
}
