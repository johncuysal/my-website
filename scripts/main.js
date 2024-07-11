window.addEventListener("DOMContentLoaded", () => {
    const mySignature = document.getElementById("my-signature");

    mySignature.addEventListener("mouseover", () => {
        mySignature.style.fill = "#" + Math.floor(Math.random() * 16777216).toString(16);
    });

    mySignature.addEventListener("mouseout", () => {
        mySignature.style.fill = "";
    });
});