import React, { useState, useRef } from 'react';
import './VideoPlayer.css';

function VideoPlayer({
  videoUrl = '/out.mp4',
  annotatedVideoUrl = '/out_annotated.mp4',
  thumbnail = null,
  isOpen = false,
  onClose = null,
  showBoundingBoxes = false,
  embedded = false
}) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [clickCount, setClickCount] = useState(0);
  const [lastClickTime, setLastClickTime] = useState(0);
  const [videoMode, setVideoMode] = useState('default'); // 'default' -> 'annotated' -> 'loop'
  const [playbackStage, setPlaybackStage] = useState(0); // 0: first default, 1: annotated, 2: loop default
  const videoRef = useRef(null);
  const annotatedVideoRef = useRef(null);

  // Use external control if provided, otherwise internal state
  const modalOpen = onClose !== null ? isOpen : isPlaying;

  const handleOpen = () => {
    if (onClose === null) {
      setIsPlaying(true);
    }
  };

  const handleClose = () => {
    // Reset playback stage when closing
    setPlaybackStage(0);
    setVideoMode('default');
    if (onClose) {
      onClose();
    } else {
      setIsPlaying(false);
    }
  };

  const handleDefaultVideoEnd = () => {
    console.log('Default video ended, playback stage:', playbackStage);
    if (playbackStage === 0) {
      // First play of out.mp4 ended, switch to annotated
      console.log('Switching to annotated video');
      setPlaybackStage(1);
      setVideoMode('annotated');
    }
    // If playbackStage is 2, video will loop naturally
  };

  const handleAnnotatedVideoEnd = () => {
    console.log('Annotated video ended, switching back to looping default');
    // Annotated video ended, go back to default and loop
    setPlaybackStage(2);
    setVideoMode('default');
  };

  // Handle modal opening - start the first video
  React.useEffect(() => {
    if (isOpen && videoRef.current && playbackStage === 0 && videoMode === 'default') {
      console.log('Modal opened, starting initial video playback');
      setTimeout(() => {
        videoRef.current.play().catch(err => console.log('Initial play error:', err));
      }, 200);
    }
  }, [isOpen]);

  // Handle video playback when mode changes
  React.useEffect(() => {
    if (videoMode === 'default' && videoRef.current && playbackStage > 0) {
      console.log('Switching to default video, stage:', playbackStage);
      const video = videoRef.current;
      setTimeout(() => {
        video.load();
        video.play().catch(err => {
          console.log('Play error on default video:', err);
          console.log('Default video src:', video.src);
        });
      }, 100);
    } else if (videoMode === 'annotated' && annotatedVideoRef.current) {
      console.log('Switching to annotated video');
      const video = annotatedVideoRef.current;
      console.log('Annotated video src:', video.src);
      setTimeout(() => {
        video.load();
        const playPromise = video.play();
        if (playPromise !== undefined) {
          playPromise.catch(err => {
            console.log('Play error on annotated video:', err);
            console.log('Video readyState:', video.readyState);
            console.log('Video networkState:', video.networkState);
            console.log('Video error:', video.error);
          });
        }
      }, 100);
    }
  }, [videoMode]);

  const handleVideoClick = (e) => {
    e.stopPropagation();
    const now = Date.now();

    // Reset click count if more than 1 second has passed since last click
    if (now - lastClickTime > 1000) {
      setClickCount(1);
      setLastClickTime(now);
      return;
    }

    // Increment click count
    const newCount = clickCount + 1;
    setClickCount(newCount);
    setLastClickTime(now);

    // Switch to annotated video after 3 clicks
    if (newCount >= 3 && videoMode === 'default') {
      setVideoMode('annotated');
      setClickCount(0); // Reset counter
    }
  };


  // Mock bounding boxes - replace with real ML model output
  const boundingBoxes = showBoundingBoxes ? [
    { x: 45, y: 30, width: 15, height: 20, confidence: 0.92, label: 'Fish' },
    { x: 65, y: 55, width: 12, height: 15, confidence: 0.87, label: 'Fish' }
  ] : [];

  // Embedded mode - render video directly without modal
  if (embedded) {
    return (
      <div className="video-container-embedded" onClick={handleVideoClick}>
        {/* Default Video */}
        <video
          ref={videoRef}
          src={videoUrl}
          controls
          playsInline
          preload="auto"
          loop={playbackStage === 2}
          onEnded={handleDefaultVideoEnd}
          className={`sonar-video-embedded ${videoMode === 'default' ? 'active' : 'inactive'}`}
        >
          Your browser does not support video playback.
        </video>

        {/* Annotated Video */}
        <video
          ref={annotatedVideoRef}
          src={annotatedVideoUrl}
          controls
          playsInline
          preload="auto"
          onEnded={handleAnnotatedVideoEnd}
          className={`sonar-video-embedded annotated ${videoMode === 'annotated' ? 'active' : 'inactive'}`}
        >
          Your browser does not support video playback.
        </video>

        {/* Bounding Box Overlays */}
        {showBoundingBoxes && (
          <div className="bounding-boxes">
            {boundingBoxes.map((box, idx) => (
              <div
                key={idx}
                className="bounding-box"
                style={{
                  left: `${box.x}%`,
                  top: `${box.y}%`,
                  width: `${box.width}%`,
                  height: `${box.height}%`
                }}
              >
                <div className="box-label">
                  {box.label} {(box.confidence * 100).toFixed(0)}%
                </div>
              </div>
            ))}
          </div>
        )}

        {showBoundingBoxes && (
          <div className="detection-info">
            <span className="detection-badge">{boundingBoxes.length} Fish Detected</span>
            <span className="ml-badge">ML Model Active</span>
          </div>
        )}
      </div>
    );
  }

  // Only render modal if external control or internal playing state
  if (onClose !== null && !isOpen) {
    return null;
  }

  return (
    <>
      {/* Thumbnail/Placeholder - only show if no external control */}
      {onClose === null && (
        <div className="video-player-thumbnail" onClick={handleOpen}>
          {thumbnail ? (
            <img src={thumbnail} alt="Sonar preview" />
          ) : (
            <div className="video-placeholder">
              <div className="play-icon">▶</div>
              <p>Click to view sonar feed</p>
            </div>
          )}
        </div>
      )}

      {/* Video Modal */}
      {modalOpen && (
        <div className="video-modal-overlay" onClick={handleClose}>
          <div className="video-modal-content" onClick={handleVideoClick}>
            <button className="video-close-btn" onClick={handleClose}>✕</button>

            <div className="video-container">
              {/* Default Video */}
              <video
                ref={videoRef}
                src={videoUrl}
                controls
                playsInline
                preload="auto"
                loop={playbackStage === 2}
                onEnded={handleDefaultVideoEnd}
                className={`sonar-video ${videoMode === 'default' ? 'active' : 'inactive'}`}
              >
                Your browser does not support video playback.
              </video>

              {/* Annotated Video */}
              <video
                ref={annotatedVideoRef}
                src={annotatedVideoUrl}
                controls
                playsInline
                preload="auto"
                onEnded={handleAnnotatedVideoEnd}
                className={`sonar-video annotated ${videoMode === 'annotated' ? 'active' : 'inactive'}`}
              >
                Your browser does not support video playback.
              </video>

              {/* Bounding Box Overlays */}
              {showBoundingBoxes && (
                <div className="bounding-boxes">
                  {boundingBoxes.map((box, idx) => (
                    <div
                      key={idx}
                      className="bounding-box"
                      style={{
                        left: `${box.x}%`,
                        top: `${box.y}%`,
                        width: `${box.width}%`,
                        height: `${box.height}%`
                      }}
                    >
                      <div className="box-label">
                        {box.label} {(box.confidence * 100).toFixed(0)}%
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {showBoundingBoxes && (
              <div className="detection-info">
                <span className="detection-badge">{boundingBoxes.length} Fish Detected</span>
                <span className="ml-badge">ML Model Active</span>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}

export default VideoPlayer;
