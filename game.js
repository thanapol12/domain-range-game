// Domain & Range Adventure Game Engine

// Game State Object
const state = {
  playerName: "จอมเวทไอแซก",
  playerClass: "knight",
  playerHP: 100,
  maxPlayerHP: 100,
  currentQuestionIndex: 0,
  questions: [],
  avatarUrl: "",
  presetChoice: "red-wizard",
  currentSlide: 1,
  isMuted: false,
  enemyHP: 100,
  maxEnemyHP: 100
};

// Web Audio API Synthesizer (for zero-dependency sound effects)
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

function playSound(type) {
  if (state.isMuted) return;
  
  // Ensure audio context is running (browsers block autoplay)
  if (audioCtx.state === 'suspended') {
    audioCtx.resume();
  }
  
  const osc = audioCtx.createOscillator();
  const gain = audioCtx.createGain();
  
  osc.connect(gain);
  gain.connect(audioCtx.destination);
  
  const now = audioCtx.currentTime;
  
  if (type === 'click') {
    osc.type = 'sine';
    osc.frequency.setValueAtTime(400, now);
    osc.frequency.exponentialRampToValueAtTime(800, now + 0.1);
    gain.gain.setValueAtTime(0.1, now);
    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.1);
    osc.start(now);
    osc.stop(now + 0.1);
  } 
  else if (type === 'correct') {
    osc.type = 'triangle';
    // Success major chord arpeggio
    osc.frequency.setValueAtTime(523.25, now); // C5
    osc.frequency.setValueAtTime(659.25, now + 0.08); // E5
    osc.frequency.setValueAtTime(783.99, now + 0.16); // G5
    osc.frequency.setValueAtTime(1046.50, now + 0.24); // C6
    gain.gain.setValueAtTime(0.15, now);
    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.4);
    osc.start(now);
    osc.stop(now + 0.4);
  } 
  else if (type === 'wrong') {
    osc.type = 'sawtooth';
    // Harsh buzz down ramp
    osc.frequency.setValueAtTime(180, now);
    osc.frequency.linearRampToValueAtTime(100, now + 0.35);
    gain.gain.setValueAtTime(0.15, now);
    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
    osc.start(now);
    osc.stop(now + 0.35);
  }
  else if (type === 'hurt') {
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(120, now);
    osc.frequency.linearRampToValueAtTime(60, now + 0.2);
    gain.gain.setValueAtTime(0.2, now);
    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.2);
    osc.start(now);
    osc.stop(now + 0.2);
  }
  else if (type === 'victory') {
    // Fanfare
    const notes = [261.63, 329.63, 392.00, 523.25, 392.00, 523.25, 659.25];
    const times = [0, 0.1, 0.2, 0.3, 0.45, 0.55, 0.7];
    notes.forEach((freq, idx) => {
      const o = audioCtx.createOscillator();
      const g = audioCtx.createGain();
      o.connect(g);
      g.connect(audioCtx.destination);
      o.type = 'triangle';
      o.frequency.setValueAtTime(freq, now + times[idx]);
      g.gain.setValueAtTime(0.1, now + times[idx]);
      g.gain.exponentialRampToValueAtTime(0.01, now + times[idx] + 0.35);
      o.start(now + times[idx]);
      o.stop(now + times[idx] + 0.45);
    });
  }
  else if (type === 'gameover') {
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(220, now);
    osc.frequency.linearRampToValueAtTime(110, now + 0.6);
    gain.gain.setValueAtTime(0.2, now);
    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.6);
    osc.start(now);
    osc.stop(now + 0.6);
  }
}

// Global Initialization
document.addEventListener('DOMContentLoaded', () => {
  setupStartScreen();
  setupTutorial();
  setupBattleArena();
});

// ==================== SCREEN 1: START SCREEN LOGIC ====================
function setupStartScreen() {
  const fileInput = document.getElementById('face-file-input');
  const uploadZone = document.getElementById('face-upload-zone');
  const previewBox = document.getElementById('upload-preview-box');
  const previewImg = document.getElementById('avatar-preview-img');
  const promptInner = document.getElementById('upload-inner-prompt');
  const btnRemoveFace = document.getElementById('btn-remove-face');
  const creationForm = document.getElementById('creation-form');
  const presetItems = document.querySelectorAll('.preset-item');

  // Preset Selection Click
  presetItems.forEach(item => {
    item.addEventListener('click', () => {
      playSound('click');
      presetItems.forEach(p => p.classList.remove('active'));
      item.classList.add('active');
      state.presetChoice = item.dataset.preset;
      updatePresetSpriteBody();
    });
  });

  // Drag and Drop files
  uploadZone.addEventListener('click', () => fileInput.click());
  
  uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('dragover');
  });

  uploadZone.addEventListener('dragleave', () => {
    uploadZone.classList.remove('dragover');
  });

  uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
      handleImageFile(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      handleImageFile(e.target.files[0]);
    }
  });

  btnRemoveFace.addEventListener('click', (e) => {
    e.stopPropagation(); // prevent triggering uploadZone click
    playSound('click');
    state.avatarUrl = "";
    previewBox.classList.add('hidden');
    promptInner.classList.remove('hidden');
    fileInput.value = "";
  });

  // Image Upload fetch request to Python Flask server
  function handleImageFile(file) {
    if (!file.type.startsWith('image/')) {
      alert("กรุณาอัปโหลดรูปภาพเท่านั้น!");
      return;
    }

    playSound('click');
    promptInner.innerHTML = `<span class="upload-icon">⏳</span><p>กำลังตรวจหาใบหน้า...</p>`;

    const formData = new FormData();
    formData.append('face_image', file);

    fetch('/upload-face', {
      method: 'POST',
      body: formData
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        state.avatarUrl = data.avatar_url;
        previewImg.src = data.avatar_url;
        promptInner.classList.add('hidden');
        previewBox.classList.remove('hidden');
      } else {
        alert("ไม่พบใบหน้าในรูป หรือประมวลผลล้มเหลว! จะใช้ระบบสุ่มใบหน้ากึ่งกลางภาพให้แทน");
        // Sometimes processing succeeds even with errors using fallback, check if url is returned
        if (data.avatar_url) {
          state.avatarUrl = data.avatar_url;
          previewImg.src = data.avatar_url;
          promptInner.classList.add('hidden');
          previewBox.classList.remove('hidden');
        } else {
          resetUploadPrompt();
        }
      }
    })
    .catch(err => {
      console.error(err);
      alert("เกิดข้อผิดพลาดในการเชื่อมต่อเซิร์ฟเวอร์! จะใช้ภาพถ่ายแบบไม่ตรวจจับใบหน้า");
      resetUploadPrompt();
    });
  }

  function resetUploadPrompt() {
    promptInner.classList.remove('hidden');
    promptInner.innerHTML = `
      <span class="upload-icon">📸</span>
      <p>ลากรูปใบหน้า หรือคลิกเพื่ออัปโหลด</p>
      <span class="upload-subtext">ประมวลผลด้วย MediaPipe Face Detection</span>
    `;
    previewBox.classList.add('hidden');
  }

  // Handle Form Submit (Transition to Onboarding Tutorial)
  creationForm.addEventListener('submit', (e) => {
    e.preventDefault();
    playSound('click');
    
    state.playerName = document.getElementById('player-name').value.trim() || "ผู้กล้า";
    state.playerClass = document.querySelector('input[name="player-class"]:checked').value;
    
    // Save details to interface
    document.getElementById('ui-player-name').textContent = state.playerName;
    
    // Apply avatar to game screen
    const faceSprite = document.getElementById('player-face-sprite');
    const faceEmoji = document.getElementById('player-emoji-face');
    
    if (state.avatarUrl) {
      faceSprite.src = state.avatarUrl;
      faceSprite.classList.remove('hidden');
      faceEmoji.classList.add('hidden');
    } else {
      faceSprite.classList.add('hidden');
      faceEmoji.classList.remove('hidden');
      // Set emoji based on class
      faceEmoji.textContent = state.playerClass === 'knight' ? '🛡️' : '🔮';
    }

    // Set sprite bodies
    const spriteContainer = document.getElementById('character-sprite-preset');
    spriteContainer.className = `character-sprite ${state.presetChoice}`;
    
    // Transition Screen
    document.getElementById('screen-start').classList.remove('active');
    document.getElementById('screen-tutorial').classList.add('active');
  });

  // Mute button control
  const btnMute = document.getElementById('btn-mute');
  btnMute.addEventListener('click', () => {
    state.isMuted = !state.isMuted;
    btnMute.querySelector('#sound-icon').textContent = state.isMuted ? '🔇' : '🔊';
    btnMute.querySelector('#sound-text').textContent = state.isMuted ? 'เสียง: ปิด' : 'เสียง: เปิด';
  });

  // Codex manual modal opening
  const btnCodex = document.getElementById('btn-codex');
  const codexModal = document.getElementById('codex-modal');
  const btnCloseCodex = document.getElementById('btn-close-codex');

  btnCodex.addEventListener('click', () => {
    playSound('click');
    codexModal.classList.remove('hidden');
  });

  btnCloseCodex.addEventListener('click', () => {
    playSound('click');
    codexModal.classList.add('hidden');
  });

  codexModal.addEventListener('click', (e) => {
    if (e.target === codexModal) {
      codexModal.classList.add('hidden');
    }
  });
}

function updatePresetSpriteBody() {
  const spriteBody = document.getElementById('player-sprite-body');
  // Dynamic visual decorations can be performed here if needed
}

// ==================== SCREEN 2: TUTORIAL SLIDES ====================
function setupTutorial() {
  const slides = document.querySelectorAll('.t-slide');
  const indicators = document.querySelectorAll('.t-indicator');
  const btnPrev = document.getElementById('btn-tut-prev');
  const btnNext = document.getElementById('btn-tut-next');
  const btnSkip = document.getElementById('btn-skip-tutorial');
  const totalSlides = slides.length;

  // Render slides function
  function showSlide(slideNum) {
    slides.forEach(slide => slide.classList.remove('active'));
    indicators.forEach(ind => ind.classList.remove('active'));
    
    document.getElementById(`t-slide-${slideNum}`).classList.add('active');
    document.querySelector(`.t-indicator[data-step="${slideNum}"]`).classList.add('active');
    
    btnPrev.disabled = slideNum === 1;
    
    if (slideNum === totalSlides) {
      btnNext.querySelector('span').textContent = "พร้อมเดินทางผจญภัย!";
    } else {
      btnNext.querySelector('span').textContent = "เข้าใจแล้ว (ถัดไป)";
    }
  }

  btnPrev.addEventListener('click', () => {
    playSound('click');
    if (state.currentSlide > 1) {
      state.currentSlide--;
      showSlide(state.currentSlide);
    }
  });

  btnNext.addEventListener('click', () => {
    playSound('click');
    if (state.currentSlide < totalSlides) {
      state.currentSlide++;
      showSlide(state.currentSlide);
    } else {
      // Start Adventure!
      finishTutorial();
    }
  });

  btnSkip.addEventListener('click', () => {
    playSound('click');
    finishTutorial();
  });

  // Mini quiz logic inside tutorial (Slide 2)
  const quizButtons = document.querySelectorAll('.quiz-opt-btn');
  const quizFeedback = document.querySelector('.quiz-feedback');

  quizButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const isCorrect = btn.dataset.correct === "true";
      
      // Clear previous styles
      quizButtons.forEach(b => {
        b.classList.remove('correct-clicked', 'wrong-clicked');
      });

      if (isCorrect) {
        playSound('correct');
        btn.classList.add('correct-clicked');
        quizFeedback.textContent = "✅ ถูกต้อง! โดเมนคือค่าตัวหน้า { 2, 5, 6 }";
        quizFeedback.style.color = "var(--green)";
      } else {
        playSound('wrong');
        btn.classList.add('wrong-clicked');
        quizFeedback.textContent = "❌ ยังไม่ถูกนะ ลองดูคำนิยามโดเมนอีกครั้ง";
        quizFeedback.style.color = "var(--red)";
      }
    });
  });

  function finishTutorial() {
    document.getElementById('screen-tutorial').classList.remove('active');
    document.getElementById('screen-battle').classList.add('active');
    loadQuestionsFromServer();
  }
}

// ==================== SCREEN 3: BATTLE ARENA ENGINE ====================
function setupBattleArena() {
  const btnSubmit = document.getElementById('btn-submit-answer');
  const answerInput = document.getElementById('answer-input');
  const btnHint = document.getElementById('btn-hint');
  const hintBox = document.getElementById('hint-box');
  const feedbackPanel = document.getElementById('feedback-panel');
  const btnNextRoom = document.getElementById('btn-next-room');

  btnSubmit.addEventListener('click', submitAnswer);
  
  answerInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      submitAnswer();
    }
  });

  btnHint.addEventListener('click', () => {
    playSound('click');
    hintBox.classList.toggle('hidden');
  });

  btnNextRoom.addEventListener('click', () => {
    playSound('click');
    feedbackPanel.classList.add('hidden');
    answerInput.value = "";
    
    // Check if monster is dead
    if (state.enemyHP <= 0) {
      // Advance to next question/stage
      state.currentQuestionIndex++;
      
      if (state.currentQuestionIndex < state.questions.length) {
        loadQuestion(state.currentQuestionIndex);
      } else {
        // Game Won! Transition to victory
        showVictoryScreen();
      }
    } else {
      // If monster is not dead, the player retries the current question (usually after a wrong answer)
      answerInput.focus();
    }
  });

  // Restart from Game Over
  document.getElementById('btn-restart').addEventListener('click', () => {
    playSound('click');
    resetGame();
    document.getElementById('screen-gameover').classList.remove('active');
    document.getElementById('screen-battle').classList.add('active');
    loadQuestion(0);
  });

  // Play Again from Victory screen
  document.getElementById('btn-play-again').addEventListener('click', () => {
    playSound('click');
    resetGame();
    document.getElementById('screen-victory').classList.remove('active');
    document.getElementById('screen-start').classList.add('active');
  });

  // Print Master Certificate
  document.getElementById('btn-print-cert').addEventListener('click', () => {
    playSound('click');
    window.print();
  });
}

function resetGame() {
  state.playerHP = 100;
  state.currentQuestionIndex = 0;
  state.currentSlide = 1;
  updatePlayerHPBar();
}

function loadQuestionsFromServer() {
  fetch('/api/questions')
    .then(res => res.json())
    .then(data => {
      state.questions = data;
      loadQuestion(0);
    })
    .catch(err => {
      console.error(err);
      alert("ไม่สามารถดึงข้อมูลโจทย์คณิตศาสตร์ได้!");
    });
}

function loadQuestion(index) {
  const q = state.questions[index];
  if (!q) return;

  // Set Stage Title
  document.getElementById('stage-title').textContent = q.title;
  
  // Set question info
  document.getElementById('ui-question-type').textContent = getQuestionTypeBadgeText(q.type);
  document.getElementById('ui-question-text').textContent = q.question_text;
  document.getElementById('hint-text').textContent = q.hint;
  document.getElementById('hint-box').classList.add('hidden'); // hide hint box by default
  
  // Setup Enemy
  document.getElementById('ui-enemy-name').textContent = q.enemy;
  state.enemyHP = q.enemy_max_hp;
  state.maxEnemyHP = q.enemy_max_hp;
  updateEnemyHPBar();
  
  // Update stage progress dots
  updateStageProgressDots(q.stage, index);

  // Set combat log
  document.getElementById('combat-log').innerHTML = `พบ <span class="text-magenta">${q.enemy}</span> ขวางประตูห้องเวทมนตร์! จงสยบมันด้วยคำตอบของโดเมนหรือเรนจ์!`;
  
  // Set Enemy emoji
  const enemyEl = document.getElementById('enemy-element');
  enemyEl.textContent = getEnemyEmoji(q.stage);

  // Render math visualizer
  renderVisualizer(q);
}

function getQuestionTypeBadgeText(type) {
  switch(type) {
    case 'choice': return 'โจทย์เลือกตอบ';
    case 'input-set': return 'วิเคราะห์คู่อันดับ/แผนภาพ';
    case 'input-interval': return 'วิเคราะห์ช่วงต่อเนื่องจากกราฟ';
    case 'input-inequality': return 'วิเคราะห์ฟังก์ชันเชิงพีชคณิต';
    default: return 'ท้าทายคณิตศาสตร์';
  }
}

function getEnemyEmoji(stage) {
  if (stage === 1) return '🌳'; // Forest elements
  if (stage === 2) return '💎'; // Cave crystal bats/spiders
  return '🧙'; // Wizard tower elements
}

function updateStageProgressDots(stageNum, activeIdx) {
  const nodes = document.querySelectorAll('.stage-node');
  nodes.forEach((node, idx) => {
    node.classList.remove('active', 'completed');
    if (idx === activeIdx) {
      node.classList.add('active');
    } else if (idx < activeIdx) {
      node.classList.add('completed');
    }
  });
}

function updatePlayerHPBar() {
  const pct = (state.playerHP / state.maxPlayerHP) * 100;
  const hpFill = document.querySelector('.player-hp');
  hpFill.style.width = `${pct}%`;
  document.getElementById('ui-player-hp-text').textContent = `${state.playerHP} / ${state.maxPlayerHP} HP`;
  
  if (pct < 30) {
    hpFill.style.background = 'linear-gradient(90deg, #d00, #ff4444)';
  } else {
    hpFill.style.background = 'linear-gradient(90deg, #ff3344, #ff6677)';
  }
}

function updateEnemyHPBar() {
  const pct = Math.max(0, (state.enemyHP / state.maxEnemyHP) * 100);
  document.querySelector('.enemy-hp').style.width = `${pct}%`;
  document.getElementById('ui-enemy-hp-text').textContent = `${Math.max(0, state.enemyHP)} / ${state.maxEnemyHP} HP`;
}

// Submit answer to backend
function submitAnswer() {
  const ansInput = document.getElementById('answer-input');
  const userAns = ansInput.value.trim();
  
  if (!userAns) {
    alert("กรุณาป้อนคำตอบก่อนทำการโจมตี!");
    return;
  }

  const q = state.questions[state.currentQuestionIndex];
  
  playSound('click');

  fetch('/api/check-answer', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question_id: q.id,
      user_answer: userAns
    })
  })
  .then(res => res.json())
  .then(data => {
    const feedbackPanel = document.getElementById('feedback-panel');
    const fIcon = document.getElementById('feedback-icon');
    const fTitle = document.getElementById('feedback-title');
    const fExp = document.getElementById('feedback-explanation-text');
    const btnText = document.getElementById('btn-next-room').querySelector('span');

    fExp.textContent = data.explanation;

    if (data.correct) {
      playSound('correct');
      // Inflict damage to enemy
      state.enemyHP = 0; // In this version, one correct answer slays the boss!
      updateEnemyHPBar();

      // Enemy hit animation
      const enemySprite = document.getElementById('enemy-sprite-container');
      enemySprite.style.animation = 'none';
      void enemySprite.offsetWidth; // trigger reflow
      enemySprite.style.animation = 'hurt 0.5s ease';
      playSound('hurt');

      fIcon.textContent = "✅";
      fTitle.textContent = "คำตอบถูกต้อง! สยบอสุรกายสำเร็จ!";
      fTitle.style.color = "var(--green)";
      btnText.textContent = "เดินทางต่อ »";
      
      document.getElementById('combat-log').innerHTML = `✨ คุณสร้างความเสียหายรุนแรง! กำจัด <span class="text-cyan">${q.enemy}</span> สำเร็จ!`;
    } 
    else {
      playSound('wrong');
      // Player takes damage
      state.playerHP -= 20;
      updatePlayerHPBar();

      // Player hit animation
      const playerSprite = document.getElementById('character-sprite-preset');
      playerSprite.style.animation = 'none';
      void playerSprite.offsetWidth;
      playerSprite.style.animation = 'hurt 0.5s ease';

      fIcon.textContent = "❌";
      fTitle.textContent = "คำตอบผิดพลาด! อสุรกายโจมตีสวนกลับ!";
      fTitle.style.color = "var(--red)";
      
      document.getElementById('combat-log').innerHTML = `💥 คาถาล้มเหลว! โดนสะท้อนพลังกลับ! สูญเสียพลังชีวิต 20 HP`;

      if (state.playerHP <= 0) {
        btnText.textContent = "สิ้นหวังแล้ว... »";
      } else {
        btnText.textContent = "ศึกษาตำราแล้วสู้ใหม่ »";
      }
    }

    // Show explanation overlay panel
    feedbackPanel.classList.remove('hidden');

    // Handle game over logic inside the continue button after slide transition
    if (state.playerHP <= 0) {
      document.getElementById('btn-next-room').onclick = () => {
        feedbackPanel.classList.add('hidden');
        showGameOverScreen();
      };
    } else {
      document.getElementById('btn-next-room').onclick = null; // restore default click
    }
  })
  .catch(err => {
    console.error(err);
    alert("เกิดข้อผิดพลาดในการสื่อสารกับระบบตรวจคำตอบ!");
  });
}

function showGameOverScreen() {
  playSound('gameover');
  document.getElementById('screen-battle').classList.remove('active');
  document.getElementById('screen-gameover').classList.add('active');
}

function showVictoryScreen() {
  playSound('victory');
  document.getElementById('screen-battle').classList.remove('active');
  document.getElementById('screen-victory').classList.add('active');
  
  // Populate Certificate
  document.getElementById('cert-player-name').textContent = state.playerName;
  
  const rank = state.playerClass === 'knight' 
    ? 'ปรมาจารย์เกราะเพชรแห่งแกน X (Grand Master of X-Domain)'
    : 'ปรมาจารย์เวทอารักษ์แห่งแกน Y (Grand Mage of Y-Range)';
  document.getElementById('cert-player-title').textContent = rank;
  
  // Copy avatar picture to cert
  const certImg = document.getElementById('cert-avatar-img');
  const certEmoji = document.getElementById('cert-avatar-emoji');
  
  if (state.avatarUrl) {
    certImg.src = state.avatarUrl;
    certImg.classList.remove('hidden');
    certEmoji.classList.add('hidden');
  } else {
    certImg.classList.add('hidden');
    certEmoji.classList.remove('hidden');
    certEmoji.textContent = state.playerClass === 'knight' ? '🛡️' : '🔮';
  }
}

// ==================== MATHEMATICAL VISUALIZER CANVAS DRAWER ====================
function renderVisualizer(q) {
  const canvas = document.getElementById('math-canvas');
  const mapContainer = document.getElementById('mapping-container');
  const algContainer = document.getElementById('algebraic-container');
  
  // Hide all visual containers
  canvas.classList.add('hidden');
  mapContainer.classList.add('hidden');
  algContainer.classList.add('hidden');
  mapContainer.innerHTML = '';
  
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  if (q.visual_type === 'ordered-pairs') {
    canvas.classList.remove('hidden');
    drawOrderedPairsOnCanvas(ctx, canvas, q.visual_data.pairs);
  } 
  else if (q.visual_type === 'mapping') {
    mapContainer.classList.remove('hidden');
    renderMappingDiagram(mapContainer, q.visual_data);
  }
  else if (q.visual_type === 'discrete-graph') {
    canvas.classList.remove('hidden');
    drawCoordinateSystem(ctx, canvas);
    drawDiscretePoints(ctx, canvas, q.visual_data.points);
  }
  else if (q.visual_type === 'continuous-graph') {
    canvas.classList.remove('hidden');
    drawCoordinateSystem(ctx, canvas);
    drawContinuousGraph(ctx, canvas, q.visual_data);
  }
  else if (q.visual_type === 'algebraic') {
    algContainer.classList.remove('hidden');
    renderAlgebraicExpression(q.visual_data.expression);
  }
}

function drawOrderedPairsOnCanvas(ctx, canvas, pairs) {
  ctx.fillStyle = '#ffffff';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  
  // Draw relation set text nicely styled
  ctx.font = "bold 20px 'Outfit', 'Kanit'";
  ctx.fillStyle = 'var(--cyan)';
  ctx.fillText("Relation R =", canvas.width / 2, 80);
  
  ctx.font = "bold 24px 'Outfit', 'Kanit'";
  ctx.fillStyle = '#ffffff';
  const pairsStr = "{ " + pairs.map(p => `(${p[0]}, ${p[1]})`).join(", ") + " }";
  ctx.fillText(pairsStr, canvas.width / 2, 150);
  
  // Draw helper boxes pointing to domain and range colors
  ctx.font = "14px 'Kanit'";
  ctx.fillStyle = '#8a94c0';
  ctx.fillText("( x = สมาชิกตัวหน้า , y = สมาชิกตัวหลัง )", canvas.width / 2, 220);
}

function renderMappingDiagram(container, data) {
  // Create Domain Set Circle
  const domSet = document.createElement('div');
  domSet.className = 'mapping-set';
  const domHeader = document.createElement('span');
  domHeader.className = 'small-label';
  domHeader.textContent = 'Set A';
  domSet.appendChild(domHeader);
  
  data.domain_set.forEach(val => {
    const node = document.createElement('div');
    node.className = 'mapping-node';
    node.id = `node-dom-${val}`;
    node.textContent = val;
    domSet.appendChild(node);
  });
  
  // Create Codomain Set Circle
  const codomSet = document.createElement('div');
  codomSet.className = 'mapping-set';
  const codomHeader = document.createElement('span');
  codomHeader.className = 'small-label';
  codomHeader.textContent = 'Set B';
  codomSet.appendChild(codomHeader);

  data.codomain_set.forEach(val => {
    const node = document.createElement('div');
    node.className = 'mapping-node magenta-node';
    node.id = `node-codom-${val}`;
    node.textContent = val;
    codomSet.appendChild(node);
  });

  container.appendChild(domSet);
  
  // Center SVG canvas to draw mapping arrows
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.style.position = 'absolute';
  svg.style.top = '0';
  svg.style.left = '0';
  svg.style.width = '100%';
  svg.style.height = '100%';
  svg.style.pointerEvents = 'none';
  container.appendChild(svg);
  
  // Draw arrows after DOM is rendered completely
  setTimeout(() => {
    const containerBBox = container.getBoundingClientRect();
    
    data.mappings.forEach(map => {
      const fromNode = document.getElementById(`node-dom-${map[0]}`);
      const toNode = document.getElementById(`node-codom-${map[1]}`);
      if (!fromNode || !toNode) return;
      
      const fromBBox = fromNode.getBoundingClientRect();
      const toBBox = toNode.getBoundingClientRect();
      
      // Calculate coordinates relative to container
      const x1 = fromBBox.right - containerBBox.left;
      const y1 = fromBBox.top + fromBBox.height / 2 - containerBBox.top;
      
      const x2 = toBBox.left - containerBBox.left;
      const y2 = toBBox.top + toBBox.height / 2 - containerBBox.top;
      
      // Create SVG arrow line
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      const controlDist = (x2 - x1) * 0.4;
      const d = `M ${x1} ${y1} C ${x1 + controlDist} ${y1}, ${x2 - controlDist} ${y2}, ${x2} ${y2}`;
      
      path.setAttribute('d', d);
      path.setAttribute('stroke', 'rgba(0, 240, 255, 0.65)');
      path.setAttribute('stroke-width', '2.5');
      path.setAttribute('fill', 'none');
      path.setAttribute('marker-end', 'url(#arrow)');
      
      // Create arrowhead marker if not exists
      let defs = svg.querySelector('defs');
      if (!defs) {
        defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
        marker.setAttribute('id', 'arrow');
        marker.setAttribute('viewBox', '0 0 10 10');
        marker.setAttribute('refX', '8');
        marker.setAttribute('refY', '5');
        marker.setAttribute('markerWidth', '6');
        marker.setAttribute('markerHeight', '6');
        marker.setAttribute('orient', 'auto-start-reverse');
        
        const pathArrow = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        pathArrow.setAttribute('d', 'M 0 1.5 L 8 5 L 0 8.5 z');
        pathArrow.setAttribute('fill', 'rgba(0, 240, 255, 0.9)');
        
        marker.appendChild(pathArrow);
        defs.appendChild(marker);
        svg.appendChild(defs);
      }
      
      svg.appendChild(path);
    });
  }, 100);

  container.appendChild(codomSet);
}

// Draw Coordinate System for Graph Puzzles
function drawCoordinateSystem(ctx, canvas) {
  const w = canvas.width;
  const h = canvas.height;
  const cx = w / 2;
  const cy = h / 2;
  
  // Draw subtle grid lines
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
  ctx.lineWidth = 1;
  const gridSize = 25; // pixel unit representing 1 unit in math
  
  // Vertical lines
  for(let x = gridSize; x < w; x += gridSize) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, h);
    ctx.stroke();
  }
  // Horizontal lines
  for(let y = gridSize; y < h; y += gridSize) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(w, y);
    ctx.stroke();
  }

  // Draw X & Y Axes
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
  ctx.lineWidth = 2;
  
  // X Axis
  ctx.beginPath();
  ctx.moveTo(10, cy);
  ctx.lineTo(w - 10, cy);
  ctx.stroke();
  
  // Y Axis
  ctx.beginPath();
  ctx.moveTo(cx, 10);
  ctx.lineTo(cx, h - 10);
  ctx.stroke();

  // Axis Labels
  ctx.fillStyle = '#fff';
  ctx.font = "bold 12px 'Outfit'";
  ctx.textAlign = 'right';
  ctx.fillText("x", w - 12, cy - 8);
  ctx.textAlign = 'left';
  ctx.fillText("y", cx + 8, 16);
  
  // Draw tick marks and numbers
  ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
  ctx.font = "10px 'Outfit'";
  ctx.textAlign = 'center';
  ctx.textBaseline = 'top';
  
  // X-axis numbers
  for(let i = -7; i <= 7; i++) {
    if (i === 0) continue;
    const xPos = cx + (i * gridSize);
    ctx.beginPath();
    ctx.moveTo(xPos, cy - 4);
    ctx.lineTo(xPos, cy + 4);
    ctx.stroke();
    
    ctx.fillText(i.toString(), xPos, cy + 6);
  }
  
  // Y-axis numbers
  ctx.textAlign = 'right';
  ctx.textBaseline = 'middle';
  for(let j = -5; j <= 5; j++) {
    if (j === 0) continue;
    const yPos = cy - (j * gridSize); // flip Y axis in math
    ctx.beginPath();
    ctx.moveTo(cx - 4, yPos);
    ctx.lineTo(cx + 4, yPos);
    ctx.stroke();
    
    ctx.fillText(j.toString(), cx - 8, yPos);
  }
}

// Convert math coordinates (e.g. 2, 3) to canvas pixel points
function mathToCanvas(mx, my, canvas) {
  const gridSize = 25;
  const cx = canvas.width / 2;
  const cy = canvas.height / 2;
  return {
    x: cx + (mx * gridSize),
    y: cy - (my * gridSize)
  };
}

function drawDiscretePoints(ctx, canvas, points) {
  points.forEach(p => {
    const pt = mathToCanvas(p[0], p[1], canvas);
    
    // Draw outer neon glow
    ctx.beginPath();
    ctx.arc(pt.x, pt.y, 8, 0, Math.PI * 2);
    ctx.fillStyle = 'var(--cyan-glow)';
    ctx.fill();

    // Draw inner circle
    ctx.beginPath();
    ctx.arc(pt.x, pt.y, 4, 0, Math.PI * 2);
    ctx.fillStyle = '#fff';
    ctx.fill();
    
    // Write coordinate text
    ctx.fillStyle = 'var(--cyan)';
    ctx.font = "bold 11px 'Outfit'";
    ctx.textAlign = 'left';
    ctx.fillText(`(${p[0]}, ${p[1]})`, pt.x + 8, pt.y - 8);
  });
}

function drawContinuousGraph(ctx, canvas, data) {
  const startPt = mathToCanvas(data.start[0], data.start[1], canvas);
  const endPt = mathToCanvas(data.end[0], data.end[1], canvas);
  
  ctx.strokeStyle = 'var(--cyan)';
  ctx.lineWidth = 4;
  ctx.shadowColor = 'var(--cyan)';
  ctx.shadowBlur = 8;
  
  if (data.type === 'line') {
    ctx.beginPath();
    ctx.moveTo(startPt.x, startPt.y);
    ctx.lineTo(endPt.x, endPt.y);
    ctx.stroke();
  } 
  else if (data.type === 'curve') {
    // Draw a nice parabolic arc
    ctx.beginPath();
    ctx.moveTo(startPt.x, startPt.y);
    
    const controlPt = mathToCanvas((data.start[0] + data.end[0])/2, data.start[1] - 0.5, canvas); // slight curve bend
    ctx.quadraticCurveTo(controlPt.x, controlPt.y, endPt.x, endPt.y);
    ctx.stroke();
  }
  
  // Reset shadow for dots
  ctx.shadowBlur = 0;

  // Draw endpoint circles (closed vs open)
  drawEndpointDot(ctx, canvas, data.start);
  drawEndpointDot(ctx, canvas, data.end);
}

function drawEndpointDot(ctx, canvas, pointInfo) {
  const pt = mathToCanvas(pointInfo[0], pointInfo[1], canvas);
  const isClosed = pointInfo[2];
  
  ctx.lineWidth = 2.5;
  if (isClosed) {
    ctx.beginPath();
    ctx.arc(pt.x, pt.y, 6, 0, Math.PI * 2);
    ctx.fillStyle = 'var(--cyan)';
    ctx.fill();
    ctx.strokeStyle = '#ffffff';
    ctx.stroke();
  } else {
    ctx.beginPath();
    ctx.arc(pt.x, pt.y, 6, 0, Math.PI * 2);
    ctx.fillStyle = '#070913'; // match card background
    ctx.fill();
    ctx.strokeStyle = 'var(--cyan)';
    ctx.stroke();
  }
  
  // Coordinate label
  ctx.fillStyle = '#ffffff';
  ctx.font = "bold 11px 'Outfit'";
  ctx.textAlign = pointInfo[0] < 0 ? 'right' : 'left';
  ctx.fillText(`(${pointInfo[0]}, ${pointInfo[1]})`, pt.x + (pointInfo[0] < 0 ? -10 : 10), pt.y - 6);
}

function renderAlgebraicExpression(expression) {
  const prettyMath = document.getElementById('pretty-math-formula');
  // Simple styling formatter for standard equations
  let formatted = expression;
  formatted = formatted.replace('\\frac{5}{x - 3}', '<div class="fraction-box"><div class="fraction-top">5</div><div class="fraction-bottom">x - 3</div></div>');
  formatted = formatted.replace('\\sqrt{x - 2}', '<span class="radical">&radic;</span><span class="radicand">x - 2</span>');
  
  prettyMath.innerHTML = formatted;
}
