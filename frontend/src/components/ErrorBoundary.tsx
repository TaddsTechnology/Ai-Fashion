import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Home, MessageCircle } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  isRetrying: boolean;
}

class ErrorBoundary extends Component<Props, State> {
  private retryCount = 0;
  private maxRetries = 3;

  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null,
    isRetrying: false
  };

  public static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
      isRetrying: false
    };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    
    this.setState({
      error,
      errorInfo
    });

    // Log to external service in production
    if (process.env.NODE_ENV === 'production') {
      this.logErrorToService(error, errorInfo);
    }
  }

  private logErrorToService = (error: Error, errorInfo: ErrorInfo) => {
    // In production, send to logging service
    const errorData = {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href
    };

    // Example: Send to logging service
    fetch('/api/log-error', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(errorData)
    }).catch(err => console.error('Failed to log error:', err));
  };

  private handleRetry = () => {
    if (this.retryCount < this.maxRetries) {
      this.setState({ isRetrying: true });
      this.retryCount++;
      
      setTimeout(() => {
        this.setState({
          hasError: false,
          error: null,
          errorInfo: null,
          isRetrying: false
        });
      }, 1000);
    }
  };

  private handleReload = () => {
    window.location.reload();
  };

  private handleGoHome = () => {
    window.location.href = '/';
  };

  private getErrorType = (error: Error | null) => {
    if (!error) return 'Unknown Error';
    
    if (error.message.includes('Network')) return 'Network Error';
    if (error.message.includes('ChunkLoadError')) return 'Loading Error';
    if (error.message.includes('TypeError')) return 'Data Error';
    if (error.message.includes('Permission')) return 'Permission Error';
    return 'Application Error';
  };

  private getUserFriendlyMessage = (error: Error | null) => {
    if (!error) return 'Something unexpected happened';
    
    const errorType = this.getErrorType(error);
    
    switch (errorType) {
      case 'Network Error':
        return 'Connection interrupted. Please check your internet and try again.';
      case 'Loading Error':
        return 'Having trouble loading your beauty profile. A quick refresh usually helps!';
      case 'Data Error':
        return 'Unable to process your color analysis. Please try again or reach out for help.';
      case 'Permission Error':
        return 'Access restricted. Please sign in or contact our support team.';
      default:
        return 'Something went wrong with your color analysis. We\'re working to fix this!';
    }
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      const errorType = this.getErrorType(this.state.error);
      const userMessage = this.getUserFriendlyMessage(this.state.error);
      const canRetry = this.retryCount < this.maxRetries;

      return (
        <div className="min-h-screen bg-gradient-to-br from-red-50 via-orange-50 to-yellow-50 flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
            <div className="mb-6">
              <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
                <AlertTriangle className="w-8 h-8 text-red-600" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                Oops! {errorType}
              </h1>
              <p className="text-gray-600 leading-relaxed">
                {userMessage}
              </p>
            </div>

            <div className="space-y-3 mb-6">
              {canRetry && (
                <button
                  onClick={this.handleRetry}
                  disabled={this.state.isRetrying}
                  className="w-full flex items-center justify-center px-4 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-medium rounded-lg hover:opacity-90 transition-all disabled:opacity-50"
                >
                  {this.state.isRetrying ? (
                    <>
                      <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      Retrying...
                    </>
                  ) : (
                    <>
                      <RefreshCw className="w-4 h-4 mr-2" />
                      Try Again ({this.maxRetries - this.retryCount} left)
                    </>
                  )}
                </button>
              )}

              <button
                onClick={this.handleReload}
                className="w-full flex items-center justify-center px-4 py-3 bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200 transition-colors"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Reload Page
              </button>

              <button
                onClick={this.handleGoHome}
                className="w-full flex items-center justify-center px-4 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-medium rounded-lg hover:opacity-90 transition-all"
              >
                <Home className="w-4 h-4 mr-2" />
                Go Home
              </button>
            </div>

            <div className="text-center">
              <p className="text-sm text-gray-500 mb-3">
                Still having trouble?
              </p>
              <a
                href="mailto:support@huematch.ai"
                className="inline-flex items-center text-purple-600 hover:text-purple-700 font-medium"
              >
                <MessageCircle className="w-4 h-4 mr-1" />
                Contact Support
              </a>
            </div>

            {process.env.NODE_ENV === 'development' && (
              <details className="mt-6 text-left">
                <summary className="text-sm text-gray-500 cursor-pointer hover:text-gray-700">
                  Developer Info
                </summary>
                <div className="mt-2 p-3 bg-gray-50 rounded-lg">
                  <pre className="text-xs text-gray-700 whitespace-pre-wrap break-all">
                    {this.state.error && this.state.error.toString()}
                    {this.state.errorInfo && this.state.errorInfo.componentStack}
                  </pre>
                </div>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
