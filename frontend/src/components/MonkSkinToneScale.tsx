import React from 'react';
import { Link } from 'react-router-dom';
import { monkSkinTones } from '../lib/data/monkSkinTones';
import { ExternalLink } from 'lucide-react';

interface MonkSkinToneScaleProps {
  selectedTone?: string;
  compact?: boolean;
}

const MonkSkinToneScale: React.FC<MonkSkinToneScaleProps> = ({ 
  selectedTone,
  compact = false
}) => {
  return (
    <div className="bg-white rounded-xl p-6 shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold text-gray-900">Monk Skin Tone Scale</h3>
        {compact && (
          <Link 
            to={selectedTone ? `/monk-colors/${selectedTone}` : '/monk-colors/Monk05'}
            className="inline-flex items-center text-purple-600 text-sm font-medium hover:text-purple-800 transition-colors"
          >
            View all colors
            <ExternalLink className="w-4 h-4 ml-1" />
          </Link>
        )}
      </div>
      
      <p className="text-gray-600 mb-4">
        {compact 
          ? "Select your skin tone to see personalized color recommendations"
          : "The Monk Skin Tone Scale is a 10-point skin tone scale designed to be more inclusive and representative of diverse skin tones."
        }
      </p>
      
      <div className={`grid ${compact ? 'grid-cols-5' : 'grid-cols-10'} gap-2`}>
        {Object.values(monkSkinTones).map((tone) => (
          <Link
            key={tone.id}
            to={`/monk-colors/${tone.id}`}
            className={`flex flex-col items-center p-2 rounded-lg transition-all ${
              selectedTone === tone.id 
                ? 'bg-purple-50 ring-2 ring-purple-500' 
                : 'hover:bg-gray-50'
            }`}
          >
            <div 
              className={`${compact ? 'w-10 h-10' : 'w-14 h-14'} rounded-full shadow-md mb-2`}
              style={{ backgroundColor: tone.hexCode }}
            />
            {!compact && (
              <>
                <span className="text-xs font-medium text-gray-700">{tone.name}</span>
                <span className="text-xs text-gray-500">{tone.hexCode}</span>
              </>
            )}
          </Link>
        ))}
      </div>
      
      {compact && (
        <div className="flex justify-between mt-4 text-xs text-gray-500">
          <span>Lighter</span>
          <span>Darker</span>
        </div>
      )}
    </div>
  );
};

export default MonkSkinToneScale; 