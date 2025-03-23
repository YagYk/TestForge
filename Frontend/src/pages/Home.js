import React, { useState, useRef, useEffect, lazy, Suspense } from 'react';
import { useInView } from 'react-intersection-observer';
import TestForm from '../components/TestForm';
import useApi from '../hooks/useApi';

// Import Spline conditionally to prevent chunk loading errors
const SplineComponent = lazy(() => {
  return import('@splinetool/react-spline')
    .catch(err => {
      console.error('Error loading Spline:', err);
      // Return a placeholder component when Spline fails to load
      return { default: () => <div className="spline-fallback">
        <h2>Interactive 3D Demo</h2>
        <p>Experience the power of mutation testing with our interactive visualization</p>
      </div> };
    });
});

function Home() {
  const [splineLoaded, setSplineLoaded] = useState(false);
  const [splineError, setSplineError] = useState(false);
  const [splineImportFailed, setSplineImportFailed] = useState(false);
  // Reduce threshold to make detection more sensitive and set triggerOnce to false
  const { ref: heroRef, inView: heroInView } = useInView({ threshold: 0.1, triggerOnce: true });
  const { ref: formRef, inView: formInView } = useInView({ 
    threshold: 0.01, // Much lower threshold to detect even slight visibility
    triggerOnce: false, // Allow re-triggering if it goes in and out of view
    rootMargin: '0px 0px -10% 0px' // Detect earlier, before fully in view
  });
  const formSectionRef = useRef(null);

  // Log when component mounts
  useEffect(() => {
    console.log('Home component mounted');
    
    // Force scroll to form section if it's not in view after a delay
    const timer = setTimeout(() => {
      if (!formInView) {
        console.log('Form not in view after timeout, forcing visibility');
        window.scrollTo({
          top: formSectionRef.current?.offsetTop - 100 || 0,
          behavior: 'smooth'
        });
      }
    }, 3000);
    
    return () => clearTimeout(timer);
  }, [formInView]);

  // Add effect to log changes in form visibility
  useEffect(() => {
    console.log('Form in view changed:', formInView);
  }, [formInView]);

  const handleSplineLoad = () => {
    setSplineLoaded(true);
    setSplineError(false); // Reset error on successful load
  };

  // Handle Spline errors
  const handleSplineError = (err) => {
    console.error("Spline loading error:", err);
    setSplineError(true);
  };

  // Implement a timeout for Spline loading
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (!splineLoaded) {
        console.warn("Spline loading timeout - forcing fallback");
        setSplineError(true);
      }
    }, 8000); // 8 second timeout

    return () => clearTimeout(timeoutId);
  }, [splineLoaded]);

  const scrollToForm = () => {
    formSectionRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="home" style={{position: 'relative'}}>
      {/* Hero Section */}
      <div className="hero" ref={heroRef} style={{ height: '80vh', maxHeight: '800px' }}>
        <div className={`hero-content ${heroInView ? 'animate-in' : ''}`}>
          <h1>Test<span>Forge</span></h1>
          <p>AI-powered mutation testing to supercharge your test suites</p>
          <button className="cta-button" onClick={scrollToForm}>Get Started</button>
        </div>

      <div className="spline-container">
          {(!splineLoaded || splineError) && (
            <div className="spline-fallback">
              <h2>Interactive 3D Demo</h2>
              <p>Experience the power of mutation testing with our interactive visualization</p>
            </div>
          )}

          {!splineError && !splineImportFailed && (
            <Suspense fallback={
              <div className="spline-fallback">
                <div className="loading-spinner"></div>
                <p>Loading 3D experience...</p>
              </div>
            }>
              <ErrorBoundary onError={() => setSplineImportFailed(true)}>
                <SplineComponent
                  scene="https://prod.spline.design/quFEM7GaRjxpPo0a/scene.splinecode"
                  onLoad={handleSplineLoad}
                  onError={handleSplineError}
                  style={{ opacity: splineLoaded ? 1 : 0, transition: 'opacity 0.5s ease' }}
                />
              </ErrorBoundary>
            </Suspense>
          )}
        </div>
      </div>
      
      {/* Debug overlay */}
      <div style={{
        position: 'fixed', 
        top: '10px', 
        right: '10px', 
        background: 'rgba(0,0,0,0.8)', 
        padding: '10px', 
        color: 'lime', 
        zIndex: 9999,
        fontSize: '12px',
        fontFamily: 'monospace'
      }}>
        <p>Debug: Home Component loaded</p>
        <p>FormInView: {formInView ? 'yes' : 'no'}</p>
        <p>HeroInView: {heroInView ? 'yes' : 'no'}</p>
        <button 
          onClick={scrollToForm} 
          style={{
            background: '#00ffcc',
            color: 'black',
            padding: '5px',
            border: 'none',
            borderRadius: '3px',
            marginTop: '5px',
            cursor: 'pointer'
          }}
        >
          Scroll to Form
        </button>
      </div>

      {/* Ensure this spacer doesn't push content too far */}
      <div className="section-spacer" style={{ height: '30px' }}></div>

      {/* Test Form Section - Force it to be visible regardless of animation state */}
      <div
        id="test-form-section"
        ref={(el) => {
          formRef.current = el;
          formSectionRef.current = el;
        }}
        className={`form-section ${formInView ? 'animate-in' : 'force-visible'}`}
        style={{
          border: '3px solid yellow',
          padding: '20px',
          margin: '20px',
          background: '#1a1a1a',
          position: 'relative',
          zIndex: 10,
          minHeight: '50vh', // Ensure it takes up enough space to be visible
          display: 'block', // Force display as block
          opacity: 1, // Force opacity to be visible
          visibility: 'visible' // Force visibility
        }}
      >
        <h2 className="section-title">Test Your Code</h2>
        <p className="section-description">
          Paste your Python code below and our AI will generate intelligent test cases based on mutations.
        </p>
        
        {/* Force visible wrapper */}
        <div style={{ 
          display: 'block',
          visibility: 'visible',
          opacity: 1,
          position: 'relative',
          zIndex: 20
        }}>
          <TestForm />
        </div>
      </div>

      <div className="section-spacer" style={{ height: '30px' }}></div>

      {/* Features Section */}
      <div className="features-section">
        <h2 className="section-title">How It Works</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">1</div>
            <h3>Mutation Analysis</h3>
            <p>We generate subtle changes (mutations) in your code that simulate potential bugs.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">2</div>
            <h3>AI Test Generation</h3>
            <p>Our AI analyzes each mutation and creates targeted test cases designed to catch them.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">3</div>
            <h3>Test Execution</h3>
            <p>We run the tests against both original and mutated code to evaluate effectiveness.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">4</div>
            <h3>Results Analysis</h3>
            <p>Get detailed insights into test quality and code coverage with actionable metrics.</p>
          </div>
        </div>
      </div>

      <div className="section-spacer"></div>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-content">
          <div className="footer-logo">
            <h3>TestForge</h3>
            <p>Mutation-Guided AI Test Generator</p>
          </div>
          <div className="footer-links">
            <a href="https://github.com/yourusername/testforge" target="_blank" rel="noopener noreferrer">
              GitHub
            </a>
            <a href="#" onClick={(e) => { e.preventDefault(); scrollToForm(); }}>
              Try it now
            </a>
          </div>
        </div>
        <div className="footer-bottom">
          <p>© {new Date().getFullYear()} TestForge. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

// Add a simple error boundary component for catching runtime errors
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error("Error in component:", error, errorInfo);
    if (this.props.onError) {
      this.props.onError(error);
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="spline-fallback">
          <h2>Interactive 3D Demo</h2>
          <p>Sorry, the 3D experience couldn't be loaded</p>
        </div>
      );
    }

    return this.props.children;
  }
}

export default Home;