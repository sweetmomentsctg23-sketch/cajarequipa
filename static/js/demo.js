"use strict";

const slides = [...document.querySelectorAll(".slide")];
const controls = [...document.querySelectorAll("[data-slide]")];

controls.forEach((button) => {
  button.addEventListener("click", () => {
    const selected = Number(button.dataset.slide);
    slides.forEach((slide, index) => {
      slide.hidden = index !== selected;
    });
    controls.forEach((control, index) => {
      control.setAttribute("aria-pressed", String(index === selected));
    });
  });
});

const dialog = document.querySelector("#demo-dialog");
document.querySelectorAll("#about-button").forEach((button) => {
  button.addEventListener("click", () => dialog.showModal());
});

const countdown = document.querySelector("#countdown");
const restartTimer = document.querySelector("#restart-timer");
const timerStatus = document.querySelector("#timer-status");
const durationSeconds = 300;
let deadline;
let timer;

function updateCountdown() {
  const remaining = Math.max(0, Math.ceil((deadline - Date.now()) / 1000));
  countdown.textContent = String(remaining);
  if (remaining === 0) {
    clearInterval(timer);
    restartTimer.hidden = false;
    timerStatus.textContent = "El conteo de demostración ha terminado. Puedes reiniciarlo.";
  }
}

function startCountdown() {
  clearInterval(timer);
  deadline = Date.now() + durationSeconds * 1000;
  restartTimer.hidden = true;
  timerStatus.textContent = "";
  timer = setInterval(updateCountdown, 250);
  updateCountdown();
}

restartTimer.addEventListener("click", () => {
  startCountdown();
  countdown.setAttribute("tabindex", "-1");
  countdown.focus();
});
startCountdown();
