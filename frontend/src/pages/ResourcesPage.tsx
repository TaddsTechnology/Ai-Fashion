import React from 'react';
import { Book, Palette, Video, Download, ExternalLink, Lightbulb, Bookmark } from 'lucide-react';
import Layout from '../components/Layout';

const ResourcesPage: React.FC = () => {
  // Resource categories
  const categories = [
    {
      title: 'Color Theory Guides',
      icon: <Palette className="w-6 h-6 text-purple-600" />,
      description: 'Learn the fundamentals of color theory and how it applies to personal styling',
      resources: [
        {
          title: 'Understanding Seasonal Color Analysis',
          description: 'A comprehensive guide to the four seasonal color types and how to identify yours',
          link: '#',
          type: 'Guide',
          icon: <Book className="w-5 h-5 text-purple-500" />
        },
        {
          title: 'The Science of Skin Tone & Color Harmony',
          description: 'Explore the scientific principles behind why certain colors complement different skin tones',
          link: '#',
          type: 'Article',
          icon: <Lightbulb className="w-5 h-5 text-purple-500" />
        },
        {
          title: 'Color Wheel Basics for Fashion & Beauty',
          description: 'Learn how to use the color wheel to create harmonious outfits and makeup looks',
          link: '#',
          type: 'Guide',
          icon: <Book className="w-5 h-5 text-purple-500" />
        }
      ]
    },
    {
      title: 'Video Tutorials',
      icon: <Video className="w-6 h-6 text-purple-600" />,
      description: 'Watch expert tutorials on color analysis and personal styling',
      resources: [
        {
          title: 'How to Determine Your Skin Undertone',
          description: 'A step-by-step video guide to identifying whether you have warm, cool, or neutral undertones',
          link: '#',
          type: 'Video',
          icon: <Video className="w-5 h-5 text-purple-500" />
        },
        {
          title: 'Makeup Color Selection Masterclass',
          description: 'Professional makeup artists share tips for choosing colors that enhance your natural beauty',
          link: '#',
          type: 'Video',
          icon: <Video className="w-5 h-5 text-purple-500" />
        },
        {
          title: 'Wardrobe Color Coordination Workshop',
          description: 'Learn how to build a cohesive wardrobe with colors that work together and flatter your skin tone',
          link: '#',
          type: 'Video',
          icon: <Video className="w-5 h-5 text-purple-500" />
        }
      ]
    },
    {
      title: 'Downloadable Tools',
      icon: <Download className="w-6 h-6 text-purple-600" />,
      description: 'Free resources to help you apply color theory to your daily life',
      resources: [
        {
          title: 'Personal Color Palette Worksheet',
          description: 'A printable worksheet to document your most flattering colors for shopping reference',
          link: '#',
          type: 'PDF',
          icon: <Download className="w-5 h-5 text-purple-500" />
        },
        {
          title: 'Seasonal Color Swatch Cards',
          description: 'Printable color swatches for each seasonal palette to take shopping with you',
          link: '#',
          type: 'PDF',
          icon: <Download className="w-5 h-5 text-purple-500" />
        },
        {
          title: 'Makeup Color Selection Guide',
          description: 'A comprehensive chart matching foundation, blush, eyeshadow, and lipstick colors to skin tones',
          link: '#',
          type: 'PDF',
          icon: <Download className="w-5 h-5 text-purple-500" />
        }
      ]
    },
    {
      title: 'External Resources',
      icon: <ExternalLink className="w-6 h-6 text-purple-600" />,
      description: 'Curated links to the best color theory resources across the web',
      resources: [
        {
          title: 'Color Psychology in Fashion',
          description: 'Research on how color choices affect mood and perception in fashion contexts',
          link: '#',
          type: 'External',
          icon: <ExternalLink className="w-5 h-5 text-purple-500" />
        },
        {
          title: 'Pantone Color Institute',
          description: 'Professional color standards and trend forecasting for fashion and beauty',
          link: '#',
          type: 'External',
          icon: <ExternalLink className="w-5 h-5 text-purple-500" />
        },
        {
          title: 'Cultural Color Meanings Around the World',
          description: 'How color symbolism varies across different cultures and contexts',
          link: '#',
          type: 'External',
          icon: <ExternalLink className="w-5 h-5 text-purple-500" />
        }
      ]
    }
  ];

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-b from-purple-50/50 to-white">
        {/* Hero Section */}
        <div className="bg-gradient-to-r from-purple-600 to-pink-500 text-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-20">
            <div className="text-center">
              <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
                Color Theory Resources
              </h1>
              <p className="mt-4 text-xl text-white max-w-3xl mx-auto">
                Explore our collection of guides, tools, and educational materials to deepen your understanding of color theory and personal styling.
              </p>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Featured Resource */}
          <div className="bg-white rounded-xl shadow-xl overflow-hidden mb-16">
            <div className="md:flex">
              <div className="md:flex-shrink-0 bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center p-8 md:w-64">
                <Bookmark className="w-20 h-20 text-white" />
              </div>
              <div className="p-8">
                <div className="uppercase tracking-wide text-sm text-pink-500 font-semibold">Featured Resource</div>
                <h2 className="mt-2 text-2xl font-bold text-gray-900">Complete Guide to Personal Color Analysis</h2>
                <p className="mt-3 text-gray-600 max-w-3xl">
                  Our comprehensive 50-page guide covers everything from identifying your skin undertone to building a wardrobe that enhances your natural coloring. This guide includes practical exercises, visual examples, and expert tips from color consultants.
                </p>
                <div className="mt-6">
                  <a
                    href="#"
                    className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-pink-600 hover:bg-pink-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-pink-500 transition-colors"
                  >
                    Download Free Guide
                    <Download className="ml-2 -mr-1 h-5 w-5" />
                  </a>
                </div>
              </div>
            </div>
          </div>

          {/* Resource Categories */}
          <div className="space-y-16">
            {categories.map((category, index) => (
              <div key={index}>
                <div className="flex items-center mb-6">
                  <div className="mr-4 bg-purple-100 p-3 rounded-lg">
                    {React.cloneElement(category.icon, { className: "w-6 h-6 text-pink-600" })}
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">{category.title}</h2>
                    <p className="text-gray-600">{category.description}</p>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {category.resources.map((resource, resourceIndex) => (
                    <div 
                      key={resourceIndex} 
                      className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-6 border border-gray-100"
                    >
                      <div className="flex items-start">
                        <div className="bg-purple-100 p-2 rounded-lg mr-4">
                          {React.cloneElement(resource.icon, { className: "w-5 h-5 text-pink-500" })}
                        </div>
                        <div>
                          <span className="text-xs font-semibold text-pink-600 uppercase tracking-wide">
                            {resource.type}
                          </span>
                          <h3 className="mt-1 text-lg font-semibold text-gray-900">{resource.title}</h3>
                          <p className="mt-2 text-gray-600 text-sm">{resource.description}</p>
                          <a 
                            href={resource.link} 
                            className="mt-4 inline-flex items-center text-sm font-medium text-pink-600 hover:text-pink-800"
                          >
                            Access Resource
                            <svg className="ml-1 w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
                            </svg>
                          </a>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Newsletter Signup */}
          <div className="mt-20 bg-gradient-to-r from-purple-100 to-pink-100 rounded-xl p-8 md:p-12">
            <div className="md:flex md:items-center md:justify-between">
              <div className="md:w-2/3">
                <h2 className="text-2xl font-bold text-gray-900">Stay Updated with New Resources</h2>
                <p className="mt-3 text-gray-600 max-w-3xl">
                  Subscribe to our newsletter to receive the latest color theory resources, guides, and tools directly in your inbox.
                </p>
              </div>
              <div className="mt-6 md:mt-0 md:w-1/3">
                <form className="sm:flex">
                  <input
                    type="email"
                    required
                    className="w-full px-5 py-3 placeholder-gray-500 focus:ring-pink-500 focus:border-pink-500 border-gray-300 rounded-md"
                    placeholder="Enter your email"
                  />
                  <button
                    type="submit"
                    className="mt-3 sm:mt-0 sm:ml-3 w-full sm:w-auto flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-white bg-pink-600 hover:bg-pink-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-pink-500"
                  >
                    Subscribe
                  </button>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default ResourcesPage; 