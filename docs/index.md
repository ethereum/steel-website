---
title: Home
hide:
  - navigation
  - toc
---

<div class="hero-container" markdown>

<div class="hero-content" markdown>

<p class="hero-label">SPECIFICATIONS & TESTING FOR THE ETHEREUM EXECUTION LAYER</p>

# The Source of Truth for Ethereum’s Execution Layer

<!--
STEEL bridges EVM research, prototyping, and production, forging [EIP](https://eips.ethereum.org/) proposals into rigorous specifications and test suites used to validate Ethereum’s diverse Execution Layer client ecosystem.

We help EIP researchers transform proposals into executable specifications and test cases, while providing the test vectors and frameworks that Execution Layer client developers rely on to verify their implementations.
-->

STEEL <span class="highlight">bridges</span> EVM research, prototyping, and production: we help <span class="highlight">researchers</span> forge [EIP](https://eips.ethereum.org/) proposals into rigorous specifications and test suites, and we provide the test vectors and frameworks that Execution Layer <span class="highlight">client developers</span> depend on to verify their implementations.

<div class="hero-buttons">
  <a href="about/" class="btn-secondary">
    More about STEEL
  </a>
  <a href="https://ethereum.github.io/execution-specs/src/ethereum/forks/osaka/__init__.py.html" class="btn-primary" target="_blank">
    Read the Specs
  </a>
  <a href="https://eest.ethereum.org/main/tests" class="btn-primary" target="_blank">
    Browse the Tests
  </a>
</div>

</div>

</div>

<style>
.hero-container {
  min-height: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 2rem 4rem 2rem;
}

.hero-content {
  max-width: 800px;
  text-align: left;
}

.hero-label {
  font-size: 0.75rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: #ff9800;
  margin-bottom: 1.5rem;
  font-weight: 600;
}

[data-md-color-scheme="default"] .hero-label {
  color: #e65100;
}

.hero-container h1 {
  font-size: clamp(2rem, 5vw, 3.5rem);
  line-height: 1.2;
  margin-bottom: 1.5rem;
  font-weight: 700;
}

.hero-container p:not(.hero-label) {
  font-size: 1.25rem;
  line-height: 1.6;
  margin-bottom: 2.5rem;
  opacity: 0.85;
}

.highlight {
  background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 700;
  position: relative;
}

[data-md-color-scheme="default"] .highlight {
  background: linear-gradient(135deg, #e65100 0%, #d84315 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-buttons {
  display: flex;
  gap: 1rem;
  justify-content: flex-start;
  flex-wrap: wrap;
}

.btn-primary {
  display: inline-block;
  padding: 0.875rem 2rem;
  background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
  color: #ffffff !important;
  text-decoration: none !important;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(255, 152, 0, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 152, 0, 0.4);
}

.btn-secondary {
  display: inline-block;
  padding: 0.875rem 2rem;
  background: transparent;
  color: #ff9800 !important;
  text-decoration: none !important;
  border: 2px solid #ff9800;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1rem;
  transition: all 0.3s ease;
}

[data-md-color-scheme="default"] .btn-secondary {
  color: #e65100 !important;
  border-color: #e65100;
}

.btn-secondary:hover {
  background: rgba(255, 152, 0, 0.1);
  transform: translateY(-2px);
}

[data-md-color-scheme="default"] .btn-secondary:hover {
  background: rgba(230, 81, 0, 0.1);
}

@media (max-width: 768px) {
  .hero-container {
    min-height: 50vh;
    padding: 3rem 1.5rem;
  }

  .hero-container h1 {
    font-size: 2rem;
  }

  .hero-container p:not(.hero-label) {
    font-size: 1.125rem;
  }
}
</style>
