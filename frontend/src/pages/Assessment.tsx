import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle, XCircle, Code, Play, ArrowRight, BookOpen } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import Editor from '@monaco-editor/react';
import { Assessment as AssessmentType, AssessmentResult, MCQOptions } from '../types';
import { apiService } from '../services/api';

const Assessment: React.FC = () => {
  const navigate = useNavigate();
  const [phase, setPhase] = useState<'setup' | 'assessment' | 'completed'>('setup');
  const [assessment, setAssessment] = useState<AssessmentType | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [userAnswer, setUserAnswer] = useState('');
  const [userCode, setUserCode] = useState(`// Write your C++ code here...
#include <iostream>
#include <vector>
using namespace std;

int main() {
    // Your implementation
    return 0;
}`);
  const [codeVerification, setCodeVerification] = useState('');
  const [isVerifying, setIsVerifying] = useState(false);
  const [results, setResults] = useState<AssessmentResult[]>([]);
  const [isSubmitting] = useState(false);
  const [questionCount, setQuestionCount] = useState(3);
  const [isGenerating, setIsGenerating] = useState(false);

  const currentQuestion = assessment?.questions[currentQuestionIndex];

  const startAssessment = async () => {
    setIsGenerating(true);
    try {
      const assessmentData = await apiService.generateAssessment(questionCount);
      setAssessment(assessmentData);
      setPhase('assessment');
      setCurrentQuestionIndex(0);
      setShowAnswer(false);
      setUserAnswer('');
      setUserCode(`// Write your C++ code here...
#include <iostream>
#include <vector>
using namespace std;

int main() {
    // Your implementation
    return 0;
}`);
      setCodeVerification('');
      setResults([]);
    } catch (error) {
      console.error('Error generating assessment:', error);
      alert('Failed to generate assessment. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };  const parseMCQQuestion = (questionText: string): { question: string; options: MCQOptions; explanation: string } => {
    const lines = questionText.split('\n').filter(line => line.trim());
    const question = lines.find(line => line.startsWith('QUESTION:'))?.replace('QUESTION:', '').trim() || '';
    const optionA = lines.find(line => line.trim().startsWith('A)'))?.replace(/^A\)/, '').trim() || '';
    const optionB = lines.find(line => line.trim().startsWith('B)'))?.replace(/^B\)/, '').trim() || '';
    const optionC = lines.find(line => line.trim().startsWith('C)'))?.replace(/^C\)/, '').trim() || '';
    const optionD = lines.find(line => line.trim().startsWith('D)'))?.replace(/^D\)/, '').trim() || '';
    const correct = lines.find(line => line.startsWith('ANSWER:'))?.replace('ANSWER:', '').trim() || '';
    const explanation = lines.find(line => line.startsWith('EXPLANATION:'))?.replace('EXPLANATION:', '').trim() || '';

    return {
      question,
      options: { A: optionA, B: optionB, C: optionC, D: optionD, correct },
      explanation
    };
  };

  const parseBlankQuestion = (questionText: string): { question: string; answers: string[]; explanation: string } => {
    const lines = questionText.split('\n').filter(line => line.trim());
    const question = lines.find(line => line.startsWith('QUESTION:'))?.replace('QUESTION:', '').trim() || '';
    const answersLine = lines.find(line => line.startsWith('ANSWERS:'))?.replace('ANSWERS:', '').trim() || '';
    const answers = answersLine.split('|').map(ans => ans.trim().toLowerCase());
    const explanation = lines.find(line => line.startsWith('EXPLANATION:'))?.replace('EXPLANATION:', '').trim() || '';

    return { question, answers, explanation };
  };

  const parseCodeQuestion = (questionText: string): { question: string; requirements: string; signature: string; example: string } => {
    const lines = questionText.split('\n').filter(line => line.trim());
    const question = lines.find(line => line.startsWith('QUESTION:'))?.replace('QUESTION:', '').trim() || '';
    const requirements = lines.find(line => line.startsWith('REQUIREMENTS:'))?.replace('REQUIREMENTS:', '').trim() || '';
    const signature = lines.find(line => line.startsWith('FUNCTION_SIGNATURE:'))?.replace('FUNCTION_SIGNATURE:', '').trim() || '';
    const exampleInput = lines.find(line => line.startsWith('EXAMPLE_INPUT:'))?.replace('EXAMPLE_INPUT:', '').trim() || '';
    const exampleOutput = lines.find(line => line.startsWith('EXAMPLE_OUTPUT:'))?.replace('EXAMPLE_OUTPUT:', '').trim() || '';
    
    return {
      question,
      requirements,
      signature,
      example: `Input: ${exampleInput}\nOutput: ${exampleOutput}`
    };
  };

  const handleMCQAnswer = (selectedOption: string) => {
    setUserAnswer(selectedOption);
    setShowAnswer(true);
  };

  const handleBlankAnswer = () => {
    setShowAnswer(true);
  };

  const handleCodeVerification = async () => {
    if (!currentQuestion || !userCode.trim()) return;
    
    setIsVerifying(true);
    try {
      const verification = await apiService.verifyCode(currentQuestion.question_text, userCode);
      setCodeVerification(verification);
      setShowAnswer(true);
    } catch (error) {
      console.error('Error verifying code:', error);
      alert('Failed to verify code. Please try again.');
    } finally {
      setIsVerifying(false);
    }
  };

  const handleDifficultyRating = (difficulty: 'easy' | 'medium' | 'hard') => {
    if (!currentQuestion) return;

    let isCorrect = false;

    if (currentQuestion.question_type === 'mcq') {
      const parsed = parseMCQQuestion(currentQuestion.question_text);
      isCorrect = userAnswer.toUpperCase() === parsed.options.correct.toUpperCase();
    } else if (currentQuestion.question_type === 'blank') {
      const parsed = parseBlankQuestion(currentQuestion.question_text);
      isCorrect = parsed.answers.some(ans => ans === userAnswer.toLowerCase().trim());
    } else if (currentQuestion.question_type === 'code') {
      isCorrect = codeVerification.includes('RESULT: YES');
    }

    const result: AssessmentResult = {
      rec_no: currentQuestion.rec_no,
      is_correct: isCorrect,
      difficulty_rating: difficulty,
    };

    setResults([...results, result]);

    // Move to next question or complete
    if (currentQuestionIndex < assessment!.questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      setShowAnswer(false);
      setUserAnswer('');
      setUserCode('');
      setCodeVerification('');
    } else {
      // Complete assessment
      completeAssessment([...results, result]);
    }
  };

  const completeAssessment = async (finalResults: AssessmentResult[]) => {
    if (!assessment) return;

    try {
      await apiService.submitAssessment(assessment.set_id, finalResults);
      setPhase('completed');
    } catch (error) {
      console.error('Error submitting assessment:', error);
      alert('Failed to submit assessment results.');
    }
  };

  const renderMCQQuestion = () => {
    if (!currentQuestion) return null;
    const parsed = parseMCQQuestion(currentQuestion.question_text);

    return (
      <div className="space-y-6">
        <div className="glass-card p-6">
          <h3 className="text-xl font-semibold text-white mb-4">{parsed.question}</h3>
          
          <div className="space-y-4">
            {(['A', 'B', 'C', 'D'] as const).map((option) => {
              const isSelected = userAnswer === option;
              const isCorrect = option === parsed.options.correct;
              const showResult = showAnswer;
              
              let buttonClass = 'w-full p-6 text-left border-2 rounded-xl transition-all duration-300 font-medium flex items-center justify-between ';
              
              if (showResult) {
                if (isCorrect) {
                  buttonClass += 'border-green-500 bg-green-500/20 text-green-300 shadow-lg shadow-green-500/20';
                } else if (isSelected && !isCorrect) {
                  buttonClass += 'border-red-500 bg-red-500/20 text-red-300 shadow-lg shadow-red-500/20';
                } else {
                  buttonClass += 'border-gray-500/50 bg-white/5 text-gray-300';
                }
              } else {
                buttonClass += isSelected 
                  ? 'border-blue-500 bg-blue-500/15 text-blue-300 shadow-lg shadow-blue-500/20 transform scale-[1.02]' 
                  : 'border-white/20 bg-white/5 text-gray-300 hover:border-blue-400 hover:bg-blue-500/10 hover:text-blue-200 hover:transform hover:scale-[1.01]';
              }

              return (
                <button
                  key={option}
                  onClick={() => !showAnswer && handleMCQAnswer(option)}
                  disabled={showAnswer}
                  className={buttonClass}
                >
                  <div className="flex items-center">
                    <span className="font-bold text-lg mr-4 w-8 h-8 rounded-full bg-white/15 flex items-center justify-center text-white backdrop-blur-sm">
                      {option}
                    </span> 
                    <span className="text-base font-medium">{parsed.options[option]}</span>
                  </div>
                  <div className="flex items-center">
                    {showResult && isCorrect && <CheckCircle className="w-6 h-6 text-green-400" />}
                    {showResult && isSelected && !isCorrect && <XCircle className="w-6 h-6 text-red-400" />}
                  </div>
                </button>
              );
            })}
          </div>

          {showAnswer && (
            <div className="mt-6 p-4 bg-blue-500/20 border border-blue-500/30 rounded-lg">
              <div className="text-blue-100 prose prose-invert prose-sm max-w-none">
                <ReactMarkdown>{parsed.explanation}</ReactMarkdown>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderBlankQuestion = () => {
    if (!currentQuestion) return null;
    const parsed = parseBlankQuestion(currentQuestion.question_text);

    return (
      <div className="space-y-6">
        <div className="glass-card p-6">
          <h3 className="text-xl font-semibold text-white mb-4">{parsed.question}</h3>
          
          <div className="space-y-4">
            <input
              type="text"
              value={userAnswer}
              onChange={(e) => setUserAnswer(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !showAnswer && handleBlankAnswer()}
              disabled={showAnswer}
              className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Type your answer here..."
            />

            {!showAnswer && (
              <button
                onClick={handleBlankAnswer}
                className="btn-primary"
                disabled={!userAnswer.trim()}
              >
                Submit Answer
              </button>
            )}

            {showAnswer && (
              <div className="space-y-4">
                <div className={`p-4 rounded-lg border ${
                  parsed.answers.some(ans => ans === userAnswer.toLowerCase().trim())
                    ? 'bg-green-500/20 border-green-500/30 text-green-300'
                    : 'bg-red-500/20 border-red-500/30 text-red-300'
                }`}>
                  <p>
                    Your answer: <strong>{userAnswer}</strong>
                    {parsed.answers.some(ans => ans === userAnswer.toLowerCase().trim()) ? (
                      <CheckCircle className="inline ml-2 w-5 h-5" />
                    ) : (
                      <XCircle className="inline ml-2 w-5 h-5" />
                    )}
                  </p>
                  <p>Correct answers: <strong>{parsed.answers.join(', ')}</strong></p>
                </div>
                
                <div className="p-4 bg-blue-500/20 border border-blue-500/30 rounded-lg">
                  <p className="text-blue-300">{parsed.explanation}</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const renderCodeQuestion = () => {
    if (!currentQuestion) return null;
    const parsed = parseCodeQuestion(currentQuestion.question_text);

    return (
      <div className="space-y-6">
        <div className="glass-card p-6">
          <h3 className="text-xl font-semibold text-white mb-4">{parsed.question}</h3>
          
          <div className="space-y-4">
            <div className="p-4 bg-blue-500/20 border border-blue-500/30 rounded-lg">
              <p className="text-blue-300 mb-2"><strong>Requirements:</strong> {parsed.requirements}</p>
              <p className="text-blue-300 mb-2"><strong>Function Signature:</strong> <code>{parsed.signature}</code></p>
              <p className="text-blue-300"><strong>Example:</strong></p>
              <pre className="text-sm mt-2 text-gray-300">{parsed.example}</pre>
            </div>

            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-300">Your C++ Implementation:</label>
              <div className="relative border border-white/20 rounded-lg overflow-hidden bg-gray-900/80 backdrop-blur-sm">
                <Editor
                  height="400px"
                  defaultLanguage="cpp"
                  value={userCode}
                  onChange={(value) => setUserCode(value || '')}
                  theme="vs-dark"
                  options={{
                    fontSize: 14,
                    fontFamily: 'JetBrains Mono, Consolas, Monaco, monospace',
                    lineNumbers: 'on',
                    minimap: { enabled: false },
                    scrollBeyondLastLine: false,
                    automaticLayout: true,
                    tabSize: 2,
                    insertSpaces: true,
                    wordWrap: 'on',
                    bracketPairColorization: { enabled: true },
                    quickSuggestions: true,
                    contextmenu: true,
                    selectOnLineNumbers: true,
                    roundedSelection: false,
                    readOnly: false,
                    cursorStyle: 'line',
                    folding: true,
                    glyphMargin: false,
                    renderLineHighlight: 'line',
                    renderWhitespace: 'selection'
                  }}
                />
                <div className="absolute top-2 right-2 text-xs text-gray-500 bg-gray-800/80 px-2 py-1 rounded pointer-events-none">
                  C++
                </div>
              </div>
            </div>

            {!showAnswer && (
              <button
                onClick={handleCodeVerification}
                disabled={!userCode.trim() || isVerifying}
                className="btn-primary flex items-center space-x-2"
              >
                {isVerifying ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Verifying...</span>
                  </>
                ) : (
                  <>
                    <Code className="w-5 h-5" />
                    <span>Verify Code</span>
                  </>
                )}
              </button>
            )}

            {showAnswer && codeVerification && (
              <div className="space-y-4">
                <div className={`p-4 rounded-lg border ${
                  codeVerification.includes('RESULT: YES')
                    ? 'bg-green-500/20 border-green-500/30'
                    : 'bg-red-500/20 border-red-500/30'
                }`}>
                  <div className="prose prose-invert prose-sm max-w-none">
                    <ReactMarkdown
                      components={{
                        p: ({ children }) => {
                          const text = children?.toString() || '';
                          // Handle RESULT: lines specially
                          if (text.startsWith('RESULT:')) {
                            const isSuccess = text.includes('YES');
                            return (
                              <div className="flex items-center mb-3">
                                {isSuccess ? (
                                  <CheckCircle className="w-5 h-5 text-green-400 mr-2" />
                                ) : (
                                  <XCircle className="w-5 h-5 text-red-400 mr-2" />
                                )}
                                <span className="font-semibold text-white">
                                  {isSuccess ? 'Solution Accepted' : 'Solution Needs Improvement'}
                                </span>
                              </div>
                            );
                          }
                          // Handle FEEDBACK: and SUGGESTIONS: with proper labels
                          if (text.startsWith('FEEDBACK:')) {
                            return (
                              <div className="mb-3">
                                <h4 className="font-semibold text-blue-300 mb-1">Feedback:</h4>
                                <p className="text-gray-200 ml-2">{text.replace('FEEDBACK:', '').trim()}</p>
                              </div>
                            );
                          }
                          if (text.startsWith('SUGGESTIONS:')) {
                            return (
                              <div className="mb-3">
                                <h4 className="font-semibold text-yellow-300 mb-1">Suggestions:</h4>
                                <p className="text-gray-200 ml-2">{text.replace('SUGGESTIONS:', '').trim()}</p>
                              </div>
                            );
                          }
                          return <p className="text-gray-200 mb-2">{children}</p>;
                        }
                      }}
                    >
                      {codeVerification}
                    </ReactMarkdown>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const renderDifficultyRating = () => {
    if (!showAnswer) return null;

    return (
      <div className="glass-card p-6">
        <h4 className="text-lg font-semibold text-white mb-4">How did you find this question?</h4>
        <div className="flex space-x-4">
          <button
            onClick={() => handleDifficultyRating('easy')}
            className="flex-1 btn-secondary bg-green-500/20 hover:bg-green-500/30 border-green-500/30"
          >
            😊 Easy
          </button>
          <button
            onClick={() => handleDifficultyRating('medium')}
            className="flex-1 btn-secondary bg-yellow-500/20 hover:bg-yellow-500/30 border-yellow-500/30"
          >
            😐 Medium
          </button>
          <button
            onClick={() => handleDifficultyRating('hard')}
            className="flex-1 btn-secondary bg-red-500/20 hover:bg-red-500/30 border-red-500/30"
          >
            😰 Hard
          </button>
        </div>
      </div>
    );
  };

  if (phase === 'setup') {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <Play className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold gradient-text mb-2">Start Assessment</h1>
          <p className="text-gray-300">
            Test your knowledge with personalized questions
          </p>
        </div>

        <div className="glass-card p-8">
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Number of Questions
              </label>
              <select
                value={questionCount}
                onChange={(e) => setQuestionCount(parseInt(e.target.value))}
                className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={1} className="bg-gray-800">1 Question</option>
                <option value={3} className="bg-gray-800">3 Questions</option>
                <option value={5} className="bg-gray-800">5 Questions</option>
                <option value={10} className="bg-gray-800">10 Questions</option>
              </select>
            </div>

            <button
              onClick={startAssessment}
              disabled={isGenerating}
              className="w-full btn-primary flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isGenerating ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Generating Questions...</span>
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  <span>Generate Assessment</span>
                </>
              )}
            </button>
          </div>
        </div>

        <div className="mt-8 glass-card p-6">
          <h3 className="text-lg font-semibold text-white mb-4">📝 How Assessment Works</h3>
          <ul className="space-y-2 text-gray-300 text-sm">
            <li>• Questions are generated based on your learning history and performance</li>
            <li>• You'll get MCQ, coding, or fill-in-the-blank questions</li>
            <li>• For coding questions, you'll use a built-in C++ editor</li>
            <li>• Rate each question's difficulty to help improve future recommendations</li>
            <li>• Your performance will be tracked to optimize learning</li>
          </ul>
        </div>
      </div>
    );
  }

  if (phase === 'assessment' && assessment && currentQuestion) {
    return (
      <div className="max-w-4xl mx-auto">
        {/* Progress */}
        <div className="glass-card p-4 mb-6">
          <div className="flex items-center justify-between">
            <span className="text-gray-300">
              Question {currentQuestionIndex + 1} of {assessment.questions.length}
            </span>
            <span className="text-gray-300">
              Topic: <span className="text-white font-semibold">{currentQuestion.topic_name}</span>
            </span>
            <span className="text-gray-300">
              Type: <span className="text-white font-semibold capitalize">{currentQuestion.question_type}</span>
            </span>
          </div>
          <div className="mt-2 w-full bg-gray-700 rounded-full h-2">
            <div 
              className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${((currentQuestionIndex + 1) / assessment.questions.length) * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Question */}
        {currentQuestion.question_type === 'mcq' && renderMCQQuestion()}
        {currentQuestion.question_type === 'blank' && renderBlankQuestion()}
        {currentQuestion.question_type === 'code' && renderCodeQuestion()}

        {/* Difficulty Rating */}
        {renderDifficultyRating()}
      </div>
    );
  }

  if (phase === 'completed') {
    const correctAnswers = results.filter(r => r.is_correct).length;
    const totalQuestions = results.length;
    const successRate = Math.round((correctAnswers / totalQuestions) * 100);

    return (
      <div className="max-w-2xl mx-auto text-center">
        <div className="glass-card p-8">
          <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-blue-600 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="w-8 h-8 text-white" />
          </div>
          
          <h1 className="text-3xl font-bold gradient-text mb-4">Assessment Complete!</h1>
          
          <div className="space-y-4 mb-8">
            <div className="text-6xl font-bold text-white">{successRate}%</div>
            <div className="text-gray-300">
              {correctAnswers} out of {totalQuestions} questions correct
            </div>
          </div>

          <div className="space-y-4">
            <button
              onClick={() => {
                setPhase('setup');
                setAssessment(null);
                setResults([]);
                setCurrentQuestionIndex(0);
              }}
              className="w-full btn-primary"
            >
              Take Another Assessment
            </button>
            
            <button
              onClick={() => navigate('/stats')}
              className="w-full btn-secondary"
            >
              View Detailed Stats
            </button>
          </div>
        </div>
      </div>
    );
  }

  return null;
};

export default Assessment;