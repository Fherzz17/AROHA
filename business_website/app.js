/**
 * Vanguard Ledger & Co.
 * Interactive Front-end Application Controller
 * Premium Accounting & Fiduciary Advisory
 */

document.addEventListener('DOMContentLoaded', () => {
  initStickyNav();
  initMobileDrawer();
  initServiceFilters();
  initRunwayCalculator();
  initTestimonialSlider();
  initModals();
  initFormSubmissions();
  initScrollAnimations();
});

/* ==========================================================================
   1. STICKY NAVIGATION & ACTIVE SCROLL SPY
   ========================================================================== */
function initStickyNav() {
  const header = document.getElementById('site-header');
  const navLinks = document.querySelectorAll('.nav-link');
  const sections = document.querySelectorAll('main section[id]');

  window.addEventListener('scroll', () => {
    // Add elevated shadow styling on scroll
    if (window.scrollY > 40) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }

    // Scroll spy active link indicator
    let currentId = '';
    const scrollPosition = window.scrollY + 120;

    sections.forEach(section => {
      const sectionTop = section.offsetTop;
      const sectionHeight = section.offsetHeight;
      if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
        currentId = section.getAttribute('id');
      }
    });

    if (currentId) {
      navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${currentId}`) {
          link.classList.add('active');
        }
      });
    }
  });

  // Smooth anchor scrolling
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const targetId = this.getAttribute('href');
      if (targetId === '#') return;

      const targetEl = document.querySelector(targetId);
      if (targetEl) {
        e.preventDefault();
        const headerOffset = 80;
        const elementPosition = targetEl.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth'
        });
      }
    });
  });
}

/* ==========================================================================
   2. MOBILE DRAWER NAVIGATION
   ========================================================================== */
function initMobileDrawer() {
  const mobileToggle = document.getElementById('mobile-toggle');
  const mobileDrawer = document.getElementById('mobile-drawer');
  const drawerClose = document.getElementById('drawer-close');
  const drawerLinks = document.querySelectorAll('.drawer-link');

  function openDrawer() {
    mobileDrawer.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeDrawer() {
    mobileDrawer.classList.remove('open');
    document.body.style.overflow = '';
  }

  if (mobileToggle) mobileToggle.addEventListener('click', openDrawer);
  if (drawerClose) drawerClose.addEventListener('click', closeDrawer);

  drawerLinks.forEach(link => {
    link.addEventListener('click', () => {
      closeDrawer();
    });
  });

  // Close when clicking outside drawer
  document.addEventListener('click', (e) => {
    if (mobileDrawer.classList.contains('open') && 
        !mobileDrawer.contains(e.target) && 
        !mobileToggle.contains(e.target)) {
      closeDrawer();
    }
  });
}

/* ==========================================================================
   3. SERVICE CATEGORY FILTERING TABS
   ========================================================================== */
function initServiceFilters() {
  const filterTabs = document.querySelectorAll('.filter-tab');
  const serviceCards = document.querySelectorAll('.service-card');

  filterTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      // Set active tab styling
      filterTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      const filterVal = tab.getAttribute('data-filter');

      // Animate and filter service cards
      serviceCards.forEach(card => {
        const category = card.getAttribute('data-category');
        if (filterVal === 'all' || category === filterVal) {
          card.style.display = 'flex';
          setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
          }, 10);
        } else {
          card.style.opacity = '0';
          card.style.transform = 'translateY(15px)';
          setTimeout(() => {
            card.style.display = 'none';
          }, 200);
        }
      });
    });
  });
}

/* ==========================================================================
   4. INTERACTIVE RUNWAY ESTIMATOR & SOLVENCY CALCULATOR
   ========================================================================== */
function initRunwayCalculator() {
  const cashInput = document.getElementById('cash-reserves');
  const burnInput = document.getElementById('monthly-burn');
  const revInput = document.getElementById('monthly-revenue');

  const displayCash = document.getElementById('display-cash');
  const displayBurn = document.getElementById('display-burn');
  const displayRev = document.getElementById('display-revenue');

  const resultRunway = document.getElementById('result-runway');
  const resultStatus = document.getElementById('result-status');
  const resultNetBurn = document.getElementById('result-net-burn');
  const resultTargetReserve = document.getElementById('result-target-reserve');

  if (!cashInput || !burnInput || !revInput) return;

  function formatCurrency(num) {
    return '$' + Number(num).toLocaleString('en-US');
  }

  function calculate() {
    const cash = parseFloat(cashInput.value);
    const grossBurn = parseFloat(burnInput.value);
    const revenue = parseFloat(revInput.value);

    // Update input display tags
    displayCash.textContent = formatCurrency(cash);
    displayBurn.textContent = formatCurrency(grossBurn);
    displayRev.textContent = formatCurrency(revenue);

    const netBurn = grossBurn - revenue;
    const targetReserve = grossBurn * 12; // Standard 12-month defensive buffer

    resultTargetReserve.textContent = `${formatCurrency(targetReserve)} (12 Mo)`;

    if (netBurn <= 0) {
      // Cash-flow positive / profitable
      resultNetBurn.textContent = `+$${Math.abs(netBurn).toLocaleString('en-US')} / mo (Positive)`;
      resultNetBurn.style.color = '#0f766e';
      resultRunway.textContent = 'Infinite / Self-Sustaining';
      resultStatus.textContent = 'Cash-Flow Positive Solvency';
      resultStatus.className = 'result-status-pill status-healthy';
    } else {
      resultNetBurn.textContent = `${formatCurrency(netBurn)} / mo`;
      resultNetBurn.style.color = '';

      const runwayMonths = cash / netBurn;
      resultRunway.textContent = `${runwayMonths.toFixed(1)} Months`;

      if (runwayMonths >= 18) {
        resultStatus.textContent = 'Optimal Solvency Horizon (18+ Mo)';
        resultStatus.className = 'result-status-pill status-healthy';
      } else if (runwayMonths >= 9) {
        resultStatus.textContent = 'Adequate Horizon (Capital Planning Recommended)';
        resultStatus.className = 'result-status-pill status-moderate';
      } else {
        resultStatus.textContent = 'Critical Burn Runway (< 9 Mo Urgent Advisory)';
        resultStatus.className = 'result-status-pill status-critical';
      }
    }
  }

  // Bind live updates
  [cashInput, burnInput, revInput].forEach(slider => {
    slider.addEventListener('input', calculate);
  });

  // Initial calculation
  calculate();
}

/* ==========================================================================
   5. TESTIMONIAL SLIDER & DOT CONTROLS
   ========================================================================== */
function initTestimonialSlider() {
  const testimonials = document.querySelectorAll('.testimonial-card');
  const dots = document.querySelectorAll('#slider-dots .dot');
  const prevBtn = document.getElementById('slider-prev');
  const nextBtn = document.getElementById('slider-next');

  if (!testimonials.length) return;

  let currentIndex = 0;
  let autoplayInterval;

  function showSlide(index) {
    if (index >= testimonials.length) index = 0;
    if (index < 0) index = testimonials.length - 1;

    currentIndex = index;

    testimonials.forEach((card, i) => {
      if (i === currentIndex) {
        card.classList.add('active');
      } else {
        card.classList.remove('active');
      }
    });

    dots.forEach((dot, i) => {
      if (i === currentIndex) {
        dot.classList.add('active');
      } else {
        dot.classList.remove('active');
      }
    });
  }

  function startAutoplay() {
    stopAutoplay();
    autoplayInterval = setInterval(() => {
      showSlide(currentIndex + 1);
    }, 7000);
  }

  function stopAutoplay() {
    if (autoplayInterval) clearInterval(autoplayInterval);
  }

  if (prevBtn) {
    prevBtn.addEventListener('click', () => {
      showSlide(currentIndex - 1);
      startAutoplay();
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', () => {
      showSlide(currentIndex + 1);
      startAutoplay();
    });
  }

  dots.forEach(dot => {
    dot.addEventListener('click', () => {
      const idx = parseInt(dot.getAttribute('data-index'), 10);
      showSlide(idx);
      startAutoplay();
    });
  });

  const sliderContainer = document.querySelector('.testimonial-slider-container');
  if (sliderContainer) {
    sliderContainer.addEventListener('mouseenter', stopAutoplay);
    sliderContainer.addEventListener('mouseleave', startAutoplay);
  }

  startAutoplay();
}

/* ==========================================================================
   6. CASE STUDY & CONSULTATION MODALS
   ========================================================================== */
const CASE_STUDIES_DATA = {
  helios: {
    tag: "Series B FinTech",
    title: "Project Helios: Restructuring Capital Efficiency to Secure $42M Growth Round",
    client: "PayStream Global Technologies • London & Amsterdam",
    heroMetric: "+3.4x Runway Extended | $42M Round Closed",
    overview: "PayStream Global approached Vanguard Ledger facing rapid enterprise scaling friction. Despite 140% YoY customer expansion, irregular vendor currency settlement and unsegmented customer acquisition overheads masked underlying unit margin compression.",
    solution: [
      "Conducted forensic Quality of Earnings (QoE) reconciliation across 4 international legal entities.",
      "Re-engineered corporate treasury hedging strategies to eliminate $1.2M in annual FX drag.",
      "Embedded an interim Fractional CFO to construct 3-statement dynamic valuation models and lead institutional due-diligence interactions with lead European VC partners."
    ],
    results: [
      "Successfully closed $42M Series B oversubscription led by Index & Balderton affiliates.",
      "Reduced net cash burn by 38% without terminating operational engineering talent.",
      "Achieved 100% clean, deficiency-free audit confirmation with zero post-closing adjustments."
    ]
  },
  greenpeak: {
    tag: "Clean Energy Infrastructure",
    title: "GreenPeak Infrastructure: $180M Multi-Asset Tax Equity Structuring",
    client: "GreenPeak Renewables LLC • Denver & Zurich",
    heroMetric: "$22.4M Direct Tax Savings | 14 Municipal Assets",
    overview: "GreenPeak required institutional tax advisory to structure a portfolio of utility-scale community solar arrays across three regulatory jurisdictions, ensuring compliance with evolving Inflation Reduction Act (IRA) tax equity guidelines.",
    solution: [
      "Constructed multi-tiered partnership flip models to allocate investment tax credits (ITC) seamlessly between sovereign wealth investors and operating entities.",
      "Formulated transfer pricing mechanisms ensuring arm’s-length compliance across cross-border hardware procurement.",
      "Built rigorous 20-year cash distribution waterfall models for consortium debt providers."
    ],
    results: [
      "Generated $22.4M in direct realized cash tax savings over the initial 36-month construction cycle.",
      "Secured investment-grade Baa1 ratings on the asset-backed debt tranche.",
      "Standardized quarterly institutional investor reporting to fulfill rigorous ESG and fiduciary covenants."
    ]
  },
  cloudsync: {
    tag: "Enterprise SaaS",
    title: "CloudSync International: Transfer Pricing & Multi-Currency Treasury Overhaul",
    client: "CloudSync Technologies Inc. • San Francisco, London & Berlin",
    heroMetric: "Close Cycle Reduced from 22 to 4 Days | 0 FX Drag",
    overview: "Experiencing rapid multi-geography growth, CloudSync's decentralized accounting systems created substantial inter-company transfer pricing risks, audit lag, and unpredictable currency hedging exposures across USD, GBP, and EUR.",
    solution: [
      "Orchestrated global ERP consolidation across three subsidiaries into a single, standardized chart of accounts.",
      "Drafted comprehensive OECD-compliant transfer pricing documentation and bilateral cost-sharing agreements.",
      "Instituted automated multi-currency sweeping rules with tier-1 banking institutions."
    ],
    results: [
      "Compressed the monthly financial close cycle from 22 days down to 4 business days.",
      "Completely eliminated $420,000 in recurring unhedged currency conversion slippage.",
      "Prepared the organization for effortless Big-4 PCAOB readiness ahead of private-equity recapitalization."
    ]
  },
  medsupply: {
    tag: "Healthcare Logistics",
    title: "MedSupply Network: Pre-IPO Working Capital & SOX Internal Controls",
    client: "MedSupply Alliance Corp • Boston & Toronto",
    heroMetric: "$4.8M Inventory Leaks Eliminated | Clean SOX 404",
    overview: "Prior to entering confidential M&A acquisition discussions with a Fortune 100 medical conglomerate, MedSupply needed an exhaustive internal controls forensic review to eliminate inventory valuation ambiguities and audit liabilities.",
    solution: [
      "Implemented automated ERP inventory reconciliation controls covering 18 central distribution warehouses.",
      "Established comprehensive Sarbanes-Oxley (SOX) Section 404 internal control testing framework.",
      "Assisted executive leadership in restating previous three fiscal periods under strict GAAP revenue recognition (ASC 606)."
    ],
    results: [
      "Eliminated $4.8M in recurring inventory phantom discrepancies.",
      "Delivered an unqualified audit opinion from Big-4 external auditors.",
      "Facilitated a transaction close at an enterprise multiple 2.2x higher than initial benchmark bids."
    ]
  }
};

window.openCaseModal = function(caseKey) {
  const modal = document.getElementById('case-study-modal');
  const container = document.getElementById('case-modal-content');
  const data = CASE_STUDIES_DATA[caseKey];

  if (!modal || !container || !data) return;

  container.innerHTML = `
    <div class="case-modal-header">
      <div class="eyebrow-pill" style="margin-bottom: 10px;">${data.tag}</div>
      <h2 class="modal-case-title">${data.title}</h2>
      <div class="modal-case-client"><strong>Client Entity:</strong> ${data.client}</div>
      <div class="modal-case-badge">${data.heroMetric}</div>
    </div>
    <div class="case-modal-body">
      <div class="case-section">
        <h4 class="case-section-heading">Strategic Context & Challenge</h4>
        <p>${data.overview}</p>
      </div>

      <div class="case-section">
        <h4 class="case-section-heading">The Vanguard Ledger Advisory Solution</h4>
        <ul class="case-solution-list">
          ${data.solution.map(item => `<li><span class="check-icon">✓</span> <div>${item}</div></li>`).join('')}
        </ul>
      </div>

      <div class="case-section">
        <h4 class="case-section-heading">Verifiable Commercial Outcomes</h4>
        <ul class="case-results-list">
          ${data.results.map(item => `<li><span class="star-icon">✦</span> <div><strong>${item}</strong></div></li>`).join('')}
        </ul>
      </div>
    </div>
    <div class="case-modal-footer">
      <button class="btn btn-primary" onclick="closeAllModals(); openConsultationModal();">
        <span>Discuss Similar Strategic Mandate</span>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
      </button>
    </div>
  `;

  modal.classList.add('active');
  document.body.style.overflow = 'hidden';
};

function openConsultationModal() {
  const modal = document.getElementById('consultation-modal');
  if (modal) {
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
  }
}

function closeAllModals() {
  document.querySelectorAll('.modal-backdrop').forEach(modal => {
    modal.classList.remove('active');
  });
  document.body.style.overflow = '';
}

function initModals() {
  const consultModal = document.getElementById('consultation-modal');
  const caseModal = document.getElementById('case-study-modal');

  const openTriggers = [
    'open-consultation-btn',
    'hero-book-btn',
    'calc-cta-btn',
    'mission-cta-btn',
    'cta-book-btn',
    'mobile-consult-btn'
  ];

  openTriggers.forEach(id => {
    const btn = document.getElementById(id);
    if (btn) {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        openConsultationModal();
      });
    }
  });

  const closeBtn1 = document.getElementById('modal-close-btn');
  const closeBtn2 = document.getElementById('case-modal-close-btn');

  if (closeBtn1) closeBtn1.addEventListener('click', closeAllModals);
  if (closeBtn2) closeBtn2.addEventListener('click', closeAllModals);

  // Close when clicking modal backdrop
  [consultModal, caseModal].forEach(modal => {
    if (modal) {
      modal.addEventListener('click', (e) => {
        if (e.target === modal) {
          closeAllModals();
        }
      });
    }
  });

  // Close on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeAllModals();
    }
  });
}

/* ==========================================================================
   7. FORM SUBMISSIONS WITH ELEGANT FEEDBACK
   ========================================================================== */
function initFormSubmissions() {
  // Consultation Request Form
  const consultForm = document.getElementById('consultation-form');
  if (consultForm) {
    consultForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const submitBtn = consultForm.querySelector('button[type="submit"]');
      const originalText = submitBtn.innerHTML;

      submitBtn.disabled = true;
      submitBtn.innerHTML = `<span>Transmitting Protocol...</span>`;

      setTimeout(() => {
        consultForm.innerHTML = `
          <div class="form-success-box">
            <div class="success-icon">✓</div>
            <h3>Executive Consultation Confirmed</h3>
            <p>Your confidential discovery request has been transmitted directly to our Managing Partner desk. A senior fiduciary officer will reach out within 4 business hours to coordinate private briefings.</p>
            <div class="success-ref">Confidential Ref: #VL-${Math.floor(100000 + Math.random() * 900000)}</div>
            <button class="btn btn-secondary" onclick="closeAllModals()">Close Briefing Window</button>
          </div>
        `;
      }, 900);
    });
  }

  // Newsletter Form
  const newsletterForm = document.getElementById('newsletter-form');
  if (newsletterForm) {
    newsletterForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const emailInput = document.getElementById('newsletter-email');
      const btn = newsletterForm.querySelector('button');
      
      btn.textContent = 'Subscribed ✓';
      btn.disabled = true;
      btn.style.background = '#0f766e';
      emailInput.value = '';
      emailInput.placeholder = 'Welcome to The Ledger Memo.';

      setTimeout(() => {
        btn.textContent = 'Subscribe';
        btn.disabled = false;
        btn.style.background = '';
        emailInput.placeholder = 'Enter corporate email address...';
      }, 5000);
    });
  }

  // Download Guide Button
  const downloadBtn = document.getElementById('download-guide-btn');
  if (downloadBtn) {
    downloadBtn.addEventListener('click', () => {
      downloadBtn.innerHTML = `<span>Preparing Dossier (PDF)...</span>`;
      setTimeout(() => {
        alert('Vanguard Ledger: 2026 Enterprise Financial Guide & Solvency Framework (PDF) generated. Download initiated under TLS encryption.');
        downloadBtn.innerHTML = `
          <span>Download 2026 Enterprise Financial Guide</span>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
        `;
      }, 700);
    });
  }
}

/* ==========================================================================
   8. INTERSECTION OBSERVER FOR SUBTLE FADE-IN MICRO-ANIMATIONS
   ========================================================================== */
function initScrollAnimations() {
  const animatedElements = document.querySelectorAll('.service-card, .project-card, .metric-card, .spotlight-project-card, .mission-statement, .about-grid');

  if (!('IntersectionObserver' in window)) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.12,
    rootMargin: '0px 0px -40px 0px'
  });

  animatedElements.forEach(el => {
    el.classList.add('reveal-on-scroll');
    observer.observe(el);
  });
}
