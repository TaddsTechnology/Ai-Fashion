import React, { useRef, useState } from 'react';
import { Camera, Upload } from 'lucide-react';
import Webcam from 'react-webcam';

interface ImageCaptureProps {
  onImageCapture: (image: string) => void;
}

const ImageCapture: React.FC<ImageCaptureProps> = ({ onImageCapture }) => {
  const [showCamera, setShowCamera] = useState(false);
  const webcamRef = useRef<Webcam>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const videoConstraints = {
    width: 720,
    height: 400,
    facingMode: "user"
  };

  const handleCapture = () => {
    if (webcamRef.current) {
      const imageSrc = webcamRef.current.getScreenshot();
      if (imageSrc) {
        onImageCapture(imageSrc);
        setShowCamera(false);
      }
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        if (typeof reader.result === 'string') {
          onImageCapture(reader.result);
        }
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="space-y-4">
      {!showCamera ? (
        <div className="grid grid-cols-2 gap-4">
          <button
            onClick={() => setShowCamera(true)}
            className="flex flex-col items-center justify-center p-8 border-2 border-dashed border-purple-300 rounded-xl hover:border-purple-500 transition-colors"
          >
            <Camera className="w-8 h-8 text-purple-500 mb-2" />
            <span className="text-sm font-medium text-gray-600">Turn on Camera</span>
          </button>

          <button
            onClick={() => fileInputRef.current?.click()}
            className="flex flex-col items-center justify-center p-8 border-2 border-dashed border-purple-300 rounded-xl hover:border-purple-500 transition-colors"
          >
            <Upload className="w-8 h-8 text-purple-500 mb-2" />
            <span className="text-sm font-medium text-gray-600">Upload from Gallery</span>
          </button>
          
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={handleFileUpload}
          />
        </div>
      ) : (
        <div className="space-y-4">
          <Webcam
            audio={false}
            ref={webcamRef}
            screenshotFormat="image/jpeg"
            videoConstraints={videoConstraints}
            className="w-full rounded-xl"
          />
          <div className="flex justify-center gap-4">
            <button
              onClick={handleCapture}
              className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
            >
              Snap a Pic!
            </button>
            <button
              onClick={() => setShowCamera(false)}
              className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
            >
              Go Back
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageCapture;