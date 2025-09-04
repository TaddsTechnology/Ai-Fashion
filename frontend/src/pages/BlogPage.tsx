import React, { useState } from 'react';
import { Calendar, Clock, User, Tag, Search, ChevronRight } from 'lucide-react';
import Layout from '../components/Layout';

const BlogPage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  
  // Blog categories
  const categories = [
    { name: 'Color Theory', count: 12 },
    { name: 'Fashion', count: 8 },
    { name: 'Beauty', count: 15 },
    { name: 'Seasonal Color Analysis', count: 7 },
    { name: 'Trends', count: 5 },
    { name: 'Personal Styling', count: 9 }
  ];

  // Featured blog post
  const featuredPost = {
    title: 'How Your Skin Tone Influences Your Perfect Color Palette',
    excerpt: 'Discover the science behind why certain colors complement different skin tones and how to identify your most flattering palette based on your unique coloring.',
    image: 'https://images.unsplash.com/photo-1549298916-b41d501d3772?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1024&q=80',
    author: 'Emma Rodriguez',
    date: 'May 15, 2023',
    readTime: '8 min read',
    category: 'Color Theory',
    slug: '#'
  };

  // Blog posts
  const blogPosts = [
    {
      title: 'The Psychology of Color in Fashion',
      excerpt: 'How different colors affect mood and perception, and why understanding color psychology can transform your wardrobe choices.',
      image: 'https://images.unsplash.com/photo-1520006403909-838d6b92c22e?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=800&q=80',
      author: 'Michael Chang',
      date: 'April 28, 2023',
      readTime: '6 min read',
      category: 'Psychology',
      slug: '#'
    },
    {
      title: 'Seasonal Color Analysis: Finding Your Perfect Palette',
      excerpt: 'A deep dive into the four seasonal color types and how to determine which one enhances your natural coloring.',
      image: 'https://images.unsplash.com/photo-1534119428213-bd2626145164?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=800&q=80',
      author: 'Sophia Williams',
      date: 'April 15, 2023',
      readTime: '10 min read',
      category: 'Seasonal Color Analysis',
      slug: '#'
    },
    {
      title: 'Makeup Colors for Different Skin Undertones',
      excerpt: 'How to choose foundation, blush, eyeshadow, and lipstick colors that complement your skin\'s undertone.',
      image: 'https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=800&q=80',
      author: 'Jessica Kim',
      date: 'April 3, 2023',
      readTime: '7 min read',
      category: 'Beauty',
      slug: '#'
    },
    {
      title: 'Building a Capsule Wardrobe with Your Personal Colors',
      excerpt: 'How to create a versatile, mix-and-match wardrobe using your most flattering color palette.',
      image: 'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=800&q=80',
      author: 'Alex Johnson',
      date: 'March 22, 2023',
      readTime: '9 min read',
      category: 'Fashion',
      slug: '#'
    },
    {
      title: 'Color Trends for 2023: What\'s In and What\'s Out',
      excerpt: 'The hottest color trends of the year and how to incorporate them into your wardrobe and beauty routine.',
      image: 'https://images.unsplash.com/photo-1576566588028-4147f3842f27?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=800&q=80',
      author: 'Taylor Martinez',
      date: 'March 10, 2023',
      readTime: '5 min read',
      category: 'Trends',
      slug: '#'
    },
    {
      title: 'The History of Color Theory in Fashion and Art',
      excerpt: 'From ancient color symbolism to modern color science: how our understanding of color has evolved through the centuries.',
      image: 'https://images.unsplash.com/photo-1579547945413-497e1b99dac0?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=800&q=80',
      author: 'David Wilson',
      date: 'February 28, 2023',
      readTime: '12 min read',
      category: 'Color Theory',
      slug: '#'
    }
  ];

  // Filter posts based on search query
  const filteredPosts = blogPosts.filter(post => 
    post.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
    post.excerpt.toLowerCase().includes(searchQuery.toLowerCase()) ||
    post.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-b from-purple-50/50 to-white">
        {/* Hero Section */}
        <div className="bg-gradient-to-r from-purple-600 to-pink-500 text-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-20">
            <div className="text-center">
              <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
                HueMatch Blog
              </h1>
              <p className="mt-4 text-xl text-white max-w-3xl mx-auto">
                Insights, tips, and inspiration for color theory, fashion, and beauty enthusiasts.
              </p>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Search Bar */}
          <div className="max-w-3xl mx-auto mb-12">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                className="block w-full pl-10 pr-3 py-4 border border-gray-300 rounded-lg focus:ring-pink-500 focus:border-pink-500"
                placeholder="Search articles..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>

          <div className="lg:grid lg:grid-cols-12 lg:gap-8">
            {/* Main Content */}
            <div className="lg:col-span-8">
              {/* Featured Post */}
              <div className="mb-12">
                <div className="relative h-96 rounded-xl overflow-hidden">
                  <img
                    src={featuredPost.image}
                    alt={featuredPost.title}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent"></div>
                  <div className="absolute bottom-0 left-0 p-6 text-white">
                    <span className="inline-block bg-pink-600 px-3 py-1 text-xs font-semibold rounded-full mb-3">
                      {featuredPost.category}
                    </span>
                    <h2 className="text-2xl md:text-3xl font-bold mb-2">{featuredPost.title}</h2>
                    <p className="text-gray-200 mb-4 line-clamp-2">{featuredPost.excerpt}</p>
                    <div className="flex items-center text-sm">
                      <User className="h-4 w-4 mr-1" />
                      <span className="mr-4">{featuredPost.author}</span>
                      <Calendar className="h-4 w-4 mr-1" />
                      <span className="mr-4">{featuredPost.date}</span>
                      <Clock className="h-4 w-4 mr-1" />
                      <span>{featuredPost.readTime}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Blog Posts Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {filteredPosts.map((post, index) => (
                  <div key={index} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
                    <div className="h-48 overflow-hidden">
                      <img
                        src={post.image}
                        alt={post.title}
                        className="w-full h-full object-cover transition-transform hover:scale-105 duration-300"
                      />
                    </div>
                    <div className="p-6">
                      <div className="flex items-center mb-2">
                        <span className="inline-block bg-purple-100 text-pink-600 px-2 py-1 text-xs font-semibold rounded-full">
                          {post.category}
                        </span>
                      </div>
                      <h3 className="text-xl font-bold text-gray-900 mb-2">{post.title}</h3>
                      <p className="text-gray-600 mb-4 line-clamp-2">{post.excerpt}</p>
                      <div className="flex items-center text-sm text-gray-500 mb-4">
                        <User className="h-4 w-4 mr-1" />
                        <span className="mr-4">{post.author}</span>
                        <Clock className="h-4 w-4 mr-1" />
                        <span>{post.readTime}</span>
                      </div>
                      <a
                        href={post.slug}
                        className="inline-flex items-center text-pink-600 hover:text-pink-800 font-medium"
                      >
                        Read Article
                        <ChevronRight className="ml-1 h-4 w-4" />
                      </a>
                    </div>
                  </div>
                ))}
              </div>

              {/* Pagination */}
              <div className="mt-12 flex justify-center">
                <nav className="inline-flex rounded-md shadow">
                  <a
                    href="#"
                    className="relative inline-flex items-center px-4 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                  >
                    Previous
                  </a>
                  <a
                    href="#"
                    className="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50"
                  >
                    1
                  </a>
                  <a
                    href="#"
                    className="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-pink-600 text-sm font-medium text-white"
                  >
                    2
                  </a>
                  <a
                    href="#"
                    className="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50"
                  >
                    3
                  </a>
                  <a
                    href="#"
                    className="relative inline-flex items-center px-4 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                  >
                    Next
                  </a>
                </nav>
              </div>
            </div>

            {/* Sidebar */}
            <div className="mt-12 lg:mt-0 lg:col-span-4">
              {/* Categories */}
              <div className="bg-white rounded-lg shadow-md p-6 mb-8">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Categories</h3>
                <ul className="space-y-2">
                  {categories.map((category, index) => (
                    <li key={index}>
                      <a
                        href="#"
                        className="flex items-center justify-between py-2 px-3 rounded-md hover:bg-purple-50 transition-colors"
                      >
                        <span className="text-gray-700 hover:text-pink-700">{category.name}</span>
                        <span className="bg-purple-100 text-pink-600 text-xs font-semibold px-2.5 py-0.5 rounded-full">
                          {category.count}
                        </span>
                      </a>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Popular Posts */}
              <div className="bg-white rounded-lg shadow-md p-6 mb-8">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Popular Posts</h3>
                <div className="space-y-4">
                  {blogPosts.slice(0, 3).map((post, index) => (
                    <a key={index} href={post.slug} className="flex items-start group">
                      <div className="flex-shrink-0 h-16 w-16 rounded-md overflow-hidden">
                        <img
                          src={post.image}
                          alt={post.title}
                          className="h-full w-full object-cover group-hover:scale-105 transition-transform duration-300"
                        />
                      </div>
                      <div className="ml-4">
                        <p className="text-sm font-medium text-gray-900 group-hover:text-pink-600 transition-colors">
                          {post.title}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">{post.date}</p>
                      </div>
                    </a>
                  ))}
                </div>
              </div>

              {/* Newsletter */}
              <div className="bg-gradient-to-br from-purple-500 to-pink-600 rounded-lg shadow-md p-6 text-white">
                <h3 className="text-lg font-bold mb-2">Subscribe to Our Newsletter</h3>
                <p className="text-purple-100 mb-4">
                  Get the latest articles, tips, and color inspiration delivered to your inbox.
                </p>
                <form>
                  <input
                    type="email"
                    required
                    className="w-full px-4 py-2 rounded-md text-gray-900 placeholder-gray-500 focus:ring-pink-300 focus:border-pink-300 mb-3"
                    placeholder="Your email address"
                  />
                  <button
                    type="submit"
                    className="w-full bg-white text-pink-600 hover:bg-purple-50 font-medium py-2 px-4 rounded-md transition-colors"
                  >
                    Subscribe
                  </button>
                </form>
              </div>

              {/* Tags */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Popular Tags</h3>
                <div className="flex flex-wrap gap-2">
                  <a href="#" className="bg-purple-100 text-pink-600 text-xs font-semibold px-3 py-1.5 rounded-full hover:bg-purple-200 transition-colors">
                    Color Theory
                  </a>
                  <a href="#" className="bg-purple-100 text-pink-600 text-xs font-semibold px-3 py-1.5 rounded-full hover:bg-purple-200 transition-colors">
                    Fashion
                  </a>
                  <a href="#" className="bg-purple-100 text-pink-600 text-xs font-semibold px-3 py-1.5 rounded-full hover:bg-purple-200 transition-colors">
                    Makeup
                  </a>
                  <a href="#" className="bg-purple-100 text-pink-600 text-xs font-semibold px-3 py-1.5 rounded-full hover:bg-purple-200 transition-colors">
                    Skin Tone
                  </a>
                  <a href="#" className="bg-purple-100 text-pink-600 text-xs font-semibold px-3 py-1.5 rounded-full hover:bg-purple-200 transition-colors">
                    Seasonal Colors
                  </a>
                  <a href="#" className="bg-purple-100 text-pink-600 text-xs font-semibold px-3 py-1.5 rounded-full hover:bg-purple-200 transition-colors">
                    Wardrobe
                  </a>
                  <a href="#" className="bg-purple-100 text-pink-600 text-xs font-semibold px-3 py-1.5 rounded-full hover:bg-purple-200 transition-colors">
                    Beauty
                  </a>
                  <a href="#" className="bg-purple-100 text-pink-600 text-xs font-semibold px-3 py-1.5 rounded-full hover:bg-purple-200 transition-colors">
                    Trends
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default BlogPage; 