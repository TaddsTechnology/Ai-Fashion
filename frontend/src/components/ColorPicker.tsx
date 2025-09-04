import React from 'react';

interface ColorPickerProps {
  colors: string[];
  selectedColor?: string;
  onChange: (color: string) => void;
}

const ColorPicker: React.FC<ColorPickerProps> = ({
  colors,
  selectedColor,
  onChange,
}) => {
  return (
    <div className="flex flex-wrap gap-2">
      {colors.map((color) => (
        <button
          key={color}
          onClick={() => onChange(color)}
          className={`w-8 h-8 rounded-full border-2 hover:scale-110 transition-transform ${
            selectedColor === color
              ? 'border-purple-600 ring-2 ring-purple-200'
              : 'border-white'
          } shadow-md`}
          style={{ backgroundColor: color }}
        />
      ))}
    </div>
  );
};

export default ColorPicker;