document.addEventListener("DOMContentLoaded", function() {
    gsap.from("header h1", { duration: 1, y: -50, opacity: 0, ease: "bounce", onComplete: () => gsap.to("header h1", { opacity: 1 }) });
    gsap.from("header p", { duration: 1, delay: 0.5, y: -50, opacity: 0, ease: "bounce", onComplete: () => gsap.to("header p", { opacity: 1 }) });
    gsap.from(".intro", { duration: 1, delay: 1, y: -50, opacity: 0, ease: "power1" });
    gsap.from(".step", { duration: 1, delay: 1.5, y: -50, opacity: 0, stagger: 0.2, ease: "power1" });
    gsap.from(".contributors li", { duration: 1, delay: 2, y: -50, opacity: 0, stagger: 0.2, ease: "power1" });


    // パララックスエフェクト
    window.addEventListener("scroll", function() {
        let scrollPosition = window.pageYOffset;
        gsap.to("header", { y: scrollPosition * 0.5, ease: "power2.out" });
    });

    // クリックアニメーション
    document.querySelectorAll('.cta-button').forEach(button => {
        button.addEventListener('click', function() {
            gsap.to(button, { duration: 0.2, x: 5, repeat: 3, yoyo: true, ease: "power1.inOut" });
        });
    });
});
