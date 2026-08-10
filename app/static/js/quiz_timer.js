/**
 * CyberAware Client-Side Quiz Runner JS
 * Strictly controls UI countdown timer, question pagination, progress bar, and submit payloads ONLY.
 * NO SCORING LOGIC IS EXECUTED IN JAVASCRIPT.
 */

document.addEventListener('DOMContentLoaded', function () {
  const quizForm = document.getElementById('quizForm');
  if (!quizForm) return;

  const questions = document.querySelectorAll('.question-step');
  const totalQuestions = questions.length;
  let currentStep = 0;
  let secondsRemaining = totalQuestions * 30; // 30 seconds per question
  let totalTimeSpent = 0;

  const timerDisplay = document.getElementById('timerDisplay');
  const progressBar = document.getElementById('quizProgressBar');
  const questionTracker = document.getElementById('questionTracker');
  const prevBtn = document.getElementById('prevBtn');
  const nextBtn = document.getElementById('nextBtn');
  const submitBtn = document.getElementById('submitBtn');
  const timeSpentInput = document.getElementById('timeSpentInput');

  // Start Timer
  const timerInterval = setInterval(function () {
    secondsRemaining--;
    totalTimeSpent++;

    const mins = Math.floor(secondsRemaining / 60);
    const secs = secondsRemaining % 60;
    if (timerDisplay) {
      timerDisplay.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }

    if (secondsRemaining <= 30 && timerDisplay) {
      timerDisplay.parentElement.classList.add('warning');
    }

    if (secondsRemaining <= 0) {
      clearInterval(timerInterval);
      if (timeSpentInput) timeSpentInput.value = totalTimeSpent;
      alert('Time has expired! Submitting your answers for server-side evaluation...');
      submitQuizServerSide();
    }
  }, 1000);

  function updateStepUI() {
    questions.forEach((q, idx) => {
      if (idx === currentStep) {
        q.style.display = 'block';
      } else {
        q.style.display = 'none';
      }
    });

    // Update Progress Bar
    const progressPercent = Math.round(((currentStep + 1) / totalQuestions) * 100);
    if (progressBar) {
      progressBar.style.width = `${progressPercent}%`;
    }
    if (questionTracker) {
      questionTracker.textContent = `Question ${currentStep + 1} of ${totalQuestions}`;
    }

    // Button States
    if (prevBtn) prevBtn.style.display = currentStep === 0 ? 'none' : 'inline-block';
    if (nextBtn) nextBtn.style.display = currentStep === totalQuestions - 1 ? 'none' : 'inline-block';
    if (submitBtn) submitBtn.style.display = currentStep === totalQuestions - 1 ? 'inline-block' : 'none';
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', function () {
      if (currentStep < totalQuestions - 1) {
        currentStep++;
        updateStepUI();
      }
    });
  }

  if (prevBtn) {
    prevBtn.addEventListener('click', function () {
      if (currentStep > 0) {
        currentStep--;
        updateStepUI();
      }
    });
  }

  // Option selection card styling
  document.querySelectorAll('.option-card').forEach(card => {
    card.addEventListener('click', function () {
      const radio = this.querySelector('input[type="radio"]');
      if (radio) {
        radio.checked = true;
        const name = radio.name;
        document.querySelectorAll(`input[name="${name}"]`).forEach(r => {
          r.closest('.option-card').classList.remove('selected');
        });
        this.classList.add('selected');
      }
    });
  });

  if (quizForm) {
    quizForm.addEventListener('submit', function (e) {
      e.preventDefault();
      clearInterval(timerInterval);
      submitQuizServerSide();
    });
  }

  function submitQuizServerSide() {
    if (timeSpentInput) timeSpentInput.value = totalTimeSpent;

    const answersPayload = {};
    const formData = new FormData(quizForm);

    for (let [key, val] of formData.entries()) {
      if (key.startswith ? key.startswith('question_') : key.indexOf('question_') === 0) {
        const qId = key.replace('question_', '');
        answersPayload[qId] = val;
      }
    }

    // Get CSRF Token
    const csrfTokenEl = document.querySelector('input[name="csrf_token"]');
    const csrfToken = csrfTokenEl ? csrfTokenEl.value : '';

    fetch(quizForm.action, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({
        answers: answersPayload,
        time_spent: totalTimeSpent
      })
    })
      .then(res => res.json())
      .then(data => {
        if (data.redirect_url) {
          window.location.href = data.redirect_url;
        } else {
          quizForm.submit();
        }
      })
      .catch(err => {
        console.error('Submission error:', err);
        quizForm.submit();
      });
  }

  // Initialize UI
  updateStepUI();
});
