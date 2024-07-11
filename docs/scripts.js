document.addEventListener("DOMContentLoaded", function() {
    gsap.from("header h1", { duration: 1, y: -50, opacity: 0, ease: "bounce" });
    gsap.from("header p", { duration: 1, delay: 0.5, y: -50, opacity: 0, ease: "bounce" });
    gsap.from(".intro", { duration: 1, delay: 1, y: -50, opacity: 0, ease: "power1" });
    gsap.from(".step", { duration: 1, delay: 1.5, y: -50, opacity: 0, stagger: 0.2, ease: "power1" });
    gsap.from(".contributors li", { duration: 1, delay: 2, y: -50, opacity: 0, stagger: 0.2, ease: "power1" });
});
