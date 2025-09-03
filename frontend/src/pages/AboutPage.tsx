import React from 'react';
import { Users, Target, Lightbulb, Code, Award, Heart } from 'lucide-react';
import Layout from '../components/Layout';

const AboutPage: React.FC = () => {
  // Team members
  const teamMembers = [
    {
      name: 'Sarah Johnson',
      role: 'Founder & CEO',
      bio: 'Color consultant with over 10 years of experience in the fashion industry. Sarah founded HueMatch to make personalized color analysis accessible to everyone.',
      image: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=256&q=80'
    },
    {
      name: 'David Chen',
      role: 'CTO',
      bio: 'AI and computer vision expert with a background in developing image recognition systems. David leads our technology team in creating cutting-edge color analysis algorithms.',
      image: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=256&q=80'
    },
    {
      name: 'Aisha Patel',
      role: 'Lead Color Consultant',
      bio: 'Certified color analyst and fashion stylist who has worked with major fashion brands. Aisha ensures our color recommendations are accurate and fashion-forward.',
      image: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=256&q=80'
    },
    {
      name: 'Marcus Williams',
      role: 'Head of Product',
      bio: 'Former beauty industry executive with expertise in product development. Marcus oversees our product roadmap and ensures we deliver exceptional user experiences.',
      image: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=256&q=80'
    },
    {
      name: 'Elena Rodriguez',
      role: 'Marketing Director',
      bio: 'Digital marketing strategist with a passion for beauty and fashion tech. Elena leads our marketing efforts to bring personalized color analysis to a wider audience.',
      image: 'https://images.unsplash.com/photo-1580489944761-15a19d654956?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=256&q=80'
    },
    {
      name: 'James Wilson',
      role: 'UX/UI Designer',
      bio: 'Award-winning designer with experience in creating intuitive interfaces for fashion and beauty applications. James ensures our app is both beautiful and user-friendly.',
      image: 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=256&q=80'
    }
  ];

  // Core values
  const coreValues = [
    {
      title: 'Personalization',
      description: 'We believe that beauty advice should be tailored to each individual\'s unique characteristics.',
      icon: <Users className="h-8 w-8 text-purple-600" />
    },
    {
      title: 'Accessibility',
      description: 'Our mission is to make professional color analysis accessible to everyone, regardless of location or budget.',
      icon: <Heart className="h-8 w-8 text-purple-600" />
    },
    {
      title: 'Innovation',
      description: 'We continuously push the boundaries of what\'s possible with AI and color theory technology.',
      icon: <Lightbulb className="h-8 w-8 text-purple-600" />
    },
    {
      title: 'Expertise',
      description: 'Our recommendations are backed by color theory science and professional color analysis expertise.',
      icon: <Award className="h-8 w-8 text-purple-600" />
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
                About HueMatch
              </h1>
              <p className="mt-4 text-xl text-white max-w-3xl mx-auto">
                We're on a mission to help everyone discover their perfect colors through AI-powered personalized analysis.
              </p>
            </div>
          </div>
        </div>

        {/* Our Story Section */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="lg:grid lg:grid-cols-2 lg:gap-16 items-center">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-6">Our Story</h2>
              <div className="space-y-4 text-gray-600">
                <p>
                  HueMatch began with a simple observation: finding colors that truly complement your unique skin tone, hair, and eyes can be challenging and often requires expensive consultations with color analysts.
                </p>
                <p>
                  Founded in 2021 by Sarah Johnson, a professional color consultant with over a decade of experience, HueMatch was born from the desire to democratize access to personalized color analysis.
                </p>
                <p>
                  By combining Sarah's expertise with cutting-edge AI technology developed by our CTO David Chen, we created an accessible platform that delivers professional-quality color recommendations to anyone with a smartphone.
                </p>
                <p>
                  Today, HueMatch has helped over 500,000 users discover their most flattering colors, transforming their wardrobes, makeup collections, and confidence in the process.
                </p>
              </div>
            </div>
            <div className="mt-12 lg:mt-0">
              <div className="relative">
                <div className="aspect-w-16 aspect-h-9 rounded-xl overflow-hidden shadow-xl">
                  <img
                    src="https://images.unsplash.com/photo-1556761175-b413da4baf72?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1074&q=80"
                    alt="HueMatch team working together"
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="absolute -bottom-6 -right-6 bg-purple-600 rounded-lg p-4 shadow-lg">
                  <Target className="h-12 w-12 text-white" />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Mission & Vision Section */}
        <div className="bg-gradient-to-r from-purple-100 to-pink-100">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">Our Mission & Vision</h2>
              <p className="max-w-3xl mx-auto text-gray-600">
                We're committed to transforming how people approach color in their daily lives.
              </p>
            </div>
            <div className="md:flex md:space-x-8">
              <div className="md:w-1/2 bg-white rounded-xl shadow-md p-8 mb-8 md:mb-0">
                <div className="inline-block p-3 bg-purple-100 rounded-lg mb-4">
                  <Target className="h-8 w-8 text-purple-600" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-4">Our Mission</h3>
                <p className="text-gray-600">
                  To democratize access to personalized color analysis through innovative technology, empowering individuals to make confident color choices that enhance their natural beauty and express their authentic selves.
                </p>
              </div>
              <div className="md:w-1/2 bg-white rounded-xl shadow-md p-8">
                <div className="inline-block p-3 bg-purple-100 rounded-lg mb-4">
                  <Lightbulb className="h-8 w-8 text-purple-600" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-4">Our Vision</h3>
                <p className="text-gray-600">
                  A world where everyone has access to personalized color guidance that celebrates their unique characteristics, reduces decision fatigue, promotes sustainable shopping habits, and ultimately helps people feel more confident in their appearance.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Core Values Section */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Our Core Values</h2>
            <p className="max-w-3xl mx-auto text-gray-600">
              These principles guide everything we do at HueMatch.
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {coreValues.map((value, index) => (
              <div key={index} className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition-shadow">
                <div className="inline-block p-3 bg-purple-100 rounded-lg mb-4">
                  {React.cloneElement(value.icon, { className: "h-8 w-8 text-pink-600" })}
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">{value.title}</h3>
                <p className="text-gray-600">{value.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Our Technology Section */}
        <div className="bg-gradient-to-r from-pink-600 to-purple-600 text-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
            <div className="lg:grid lg:grid-cols-2 lg:gap-16 items-center">
              <div>
                <h2 className="text-3xl font-bold mb-6">Our Technology</h2>
                <div className="space-y-4">
                  <p>
                    At the heart of HueMatch is our proprietary AI-powered color analysis technology that combines computer vision, machine learning, and color theory expertise.
                  </p>
                  <p>
                    Our algorithms analyze over 50 distinct data points from your uploaded photos, including subtle variations in skin tone, undertones, contrast levels, and facial features.
                  </p>
                  <p>
                    This data is processed through our color matching engine, which has been trained on thousands of professional color analyses to provide recommendations that rival in-person consultations.
                  </p>
                  <p>
                    We continuously refine our technology through user feedback and collaboration with professional color consultants to ensure the highest accuracy in our recommendations.
                  </p>
                </div>
              </div>
              <div className="mt-12 lg:mt-0 flex justify-center">
                <div className="relative">
                  <div className="bg-white/10 backdrop-blur-sm rounded-xl p-8 shadow-xl">
                    <Code className="h-32 w-32 text-white/80" />
                  </div>
                  <div className="absolute -bottom-4 -right-4 bg-pink-500 rounded-lg p-3 shadow-lg">
                    <Lightbulb className="h-8 w-8 text-white" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Team Section */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Meet Our Team</h2>
            <p className="max-w-3xl mx-auto text-gray-600">
              The passionate experts behind HueMatch who are dedicated to helping you discover your perfect colors.
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {teamMembers.map((member, index) => (
              <div key={index} className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-lg transition-shadow">
                <div className="h-64 overflow-hidden">
                  <img
                    src={member.image}
                    alt={member.name}
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="p-6">
                  <h3 className="text-xl font-bold text-gray-900">{member.name}</h3>
                  <p className="text-purple-600 font-medium mb-3">{member.role}</p>
                  <p className="text-gray-600">{member.bio}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Join Us Section */}
        <div className="bg-gradient-to-r from-purple-100 to-pink-100">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
            <div className="lg:grid lg:grid-cols-2 lg:gap-16 items-center">
              <div>
                <h2 className="text-3xl font-bold text-gray-900 mb-6">Join Our Journey</h2>
                <div className="space-y-4 text-gray-600">
                  <p>
                    We're always looking for talented individuals who are passionate about color theory, technology, and helping people look and feel their best.
                  </p>
                  <p>
                    At HueMatch, you'll work with a diverse team of experts in a collaborative environment where innovation and creativity are encouraged.
                  </p>
                  <p>
                    Whether you're a developer, color consultant, UX designer, or marketing specialist, we'd love to hear from you.
                  </p>
                </div>
                <div className="mt-8">
                  <a
                    href="#"
                    className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-pink-600 hover:bg-pink-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-pink-500 transition-colors"
                  >
                    View Open Positions
                  </a>
                </div>
              </div>
              <div className="mt-12 lg:mt-0">
                <div className="bg-white rounded-xl shadow-xl p-8">
                  <div className="aspect-w-16 aspect-h-9 rounded-lg overflow-hidden">
                    <img
                      src="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1074&q=80"
                      alt="HueMatch team collaborating"
                      className="w-full h-full object-cover"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default AboutPage; 