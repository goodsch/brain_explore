<script lang="ts">
    /**
     * ForgeMode - Structured Thinking Interface (Layer 2)
     *
     * Template-driven AI-guided questioning with 5 specialized thinking modes:
     * - Learning: Understand new concepts (Mechanism Map)
     * - Articulating: Clarify vague intuitions (Clarify Intuition)
     * - Planning: Develop action strategies
     * - Ideating: Generate creative options
     * - Reflecting: Personal insight
     *
     * Features split view: conversation (left) + template progress (right)
     */
    import { onMount, createEventDispatcher } from 'svelte';
    import { showMessage, getFrontend, fetchSyncPost } from 'siyuan';
    import { createSessionDocument } from '../utils/siyuan-structure';

    export let backendUrl: string;

    const dispatch = createEventDispatcher();

    // Thinking modes with template mappings
    type ThinkingMode = 'learning' | 'articulating' | 'planning' | 'ideating' | 'reflecting';

    const THINKING_MODES: Record<ThinkingMode, {
        name: string;
        description: string;
        aiPrompt: string;
        icon: string;
        templateId?: string;
    }> = {
        learning: {
            name: 'Learning',
            description: 'Understand a new concept',
            aiPrompt: 'Use Socratic questioning to help explore and understand this concept deeply. Ask probing questions that reveal assumptions and connections.',
            icon: '📚',
            templateId: 'learning-mechanism-map'
        },
        articulating: {
            name: 'Articulating',
            description: 'Clarify a vague intuition',
            aiPrompt: 'Help articulate vague thoughts precisely. Mirror back what you hear, use precise language, and help crystallize unclear ideas.',
            icon: '💭',
            templateId: 'articulating-clarify-intuition'
        },
        planning: {
            name: 'Planning',
            description: 'Develop an action strategy',
            aiPrompt: 'Help develop a clear action plan. Clarify goals, identify obstacles, break down steps, and ensure the plan is actionable.',
            icon: '🎯'
        },
        ideating: {
            name: 'Ideating',
            description: 'Generate creative options',
            aiPrompt: 'Encourage divergent thinking. Generate many possibilities, explore unconventional options, and help expand the solution space.',
            icon: '💡'
        },
        reflecting: {
            name: 'Reflecting',
            description: 'Gain personal insight',
            aiPrompt: 'Use phenomenological questioning to explore personal experience. Focus on feelings, meanings, and self-understanding.',
            icon: '🪞'
        }
    };

    // Template structure (fetched from backend)
    interface TemplateSection {
        id: string;
        prompt: string;
        input_type: string | null;
        ai_behavior: string | null;
        required: boolean;
    }

    interface Template {
        id: string;
        mode: string;
        name: string;
        description: string;
        sections: TemplateSection[];
        graph_mapping: any;
    }

    // State
    let sessionId: string | null = null;
    let status: 'idle' | 'starting' | 'active' | 'error' = 'idle';
    let messages: Array<{role: string, content: string}> = [];
    let errorMsg = '';
    let inputText = '';
    let isLoading = false;
    let isMobile = false;

    // Thinking mode state
    let selectedMode: ThinkingMode = 'learning';
    let sessionTopic = '';

    // Template-driven session state
    let template: Template | null = null;
    let currentSectionIndex = 0;
    let sectionResponses: Record<string, string> = {};
    let showProgress = false;

    // Question engine state
    let detectedState: string = 'exploring';
    let currentApproach: string = 'socratic';

    // Question class tracking for session documents
    interface ClassifiedQuestion {
        question: string;
        question_class: string;
        approach: string;
    }
    let questionClassesUsed: string[] = [];
    let lastQuestionClass: string | null = null;

    // Question-response dialogue state (INTERACTIVE - not passive display)
    interface PendingQuestion {
        question: string;
        questionClass: string;
        approach: string;
        generatedAt: number;
    }
    let pendingQuestion: PendingQuestion | null = null;
    let questionResponseText = '';
    let isProcessingQuestion = false;

    // Question-response history for session transcript
    interface QuestionResponse {
        question: string;
        questionClass: string;
        userResponse: string;
        followUpQuestion?: string;
        timestamp: number;
    }
    let questionResponseHistory: QuestionResponse[] = [];

    // Question class display names
    const QUESTION_CLASS_LABELS: Record<string, { label: string; emoji: string; color: string }> = {
        schema_probe: { label: 'Structure', emoji: '🏗️', color: '#4a90d9' },
        boundary: { label: 'Boundary', emoji: '🔲', color: '#7b68ee' },
        dimensional: { label: 'Dimensional', emoji: '📐', color: '#20b2aa' },
        causal: { label: 'Causal', emoji: '⚡', color: '#f4a460' },
        counterfactual: { label: 'What-If', emoji: '🔮', color: '#da70d6' },
        anchor: { label: 'Anchor', emoji: '⚓', color: '#3cb371' },
        perspective_shift: { label: 'Perspective', emoji: '👁️', color: '#cd853f' },
        meta_cognitive: { label: 'Meta', emoji: '🧠', color: '#778899' },
        reflective_synthesis: { label: 'Synthesis', emoji: '🔗', color: '#6495ed' },
    };

    // Class-specific cognitive hints (ACTIVE guidance, not just decoration)
    const QUESTION_CLASS_HINTS: Record<string, { hint: string; prompt: string; responseStarter?: string }> = {
        schema_probe: {
            hint: "This question asks you to surface hidden structure",
            prompt: "Try listing the main categories, components, or buckets",
            responseStarter: "The main parts are..."
        },
        boundary: {
            hint: "This question asks you to clarify edges and limits",
            prompt: "Think about what's NOT included, where this ends",
            responseStarter: "This is different from... because..."
        },
        dimensional: {
            hint: "This question asks you to position on a spectrum",
            prompt: "Consider axes like low-high, simple-complex, or concrete-abstract",
            responseStarter: "On a scale from X to Y, this is..."
        },
        causal: {
            hint: "This question asks about mechanisms and sequences",
            prompt: "Trace the chain: what causes what? What must happen first?",
            responseStarter: "This happens because..."
        },
        counterfactual: {
            hint: "This question invites 'what if' exploration",
            prompt: "Imagine the opposite were true, or a key element was removed",
            responseStarter: "If that weren't true, then..."
        },
        anchor: {
            hint: "This question asks for concrete grounding",
            prompt: "Give a specific example from your actual experience",
            responseStarter: "A specific time this happened was..."
        },
        perspective_shift: {
            hint: "This question asks you to change viewpoints",
            prompt: "Consider how someone else would see this, or zoom in/out",
            responseStarter: "From X's perspective, this looks like..."
        },
        meta_cognitive: {
            hint: "This question checks in on your thinking process",
            prompt: "Notice how confident, stuck, or energized you feel right now",
            responseStarter: "Right now I'm feeling... about this because..."
        },
        reflective_synthesis: {
            hint: "This question asks you to integrate and connect",
            prompt: "What's the main thread? How do the pieces fit together?",
            responseStarter: "The core insight is..."
        }
    };

    // Mode transition suggestions based on question patterns
    const CLASS_TO_SUGGESTED_MODE: Record<string, ThinkingMode[]> = {
        schema_probe: ['learning'],
        boundary: ['articulating'],
        dimensional: ['planning'],
        causal: ['learning'],
        counterfactual: ['ideating'],
        anchor: ['reflecting'],
        perspective_shift: ['ideating'],
        meta_cognitive: ['reflecting'],
        reflective_synthesis: ['articulating']
    };

    // Cognitive guidance state
    let showQuestionHint = false;
    let questionHintExpanded = false;
    let classUsageCount: Record<string, number> = {};
    let modeTransitionSuggestion: { targetMode: ThinkingMode; reason: string } | null = null;

    // Cognitive coverage tracking (4 dimensions)
    interface CoverageStats {
        structureSurfacing: number;   // schema_probe + boundary + dimensional
        mechanismExploration: number; // causal + counterfactual
        groundingPerspective: number; // anchor + perspective_shift
        metaLevel: number;            // meta_cognitive + reflective_synthesis
    }
    let coverageStats: CoverageStats = {
        structureSurfacing: 0,
        mechanismExploration: 0,
        groundingPerspective: 0,
        metaLevel: 0
    };

    const USER_ID = 'chris';

    // Update cognitive coverage stats when a question class is used
    function updateCoverageStats(questionClass: string): void {
        const structureClasses = ['schema_probe', 'boundary', 'dimensional'];
        const mechanismClasses = ['causal', 'counterfactual'];
        const groundingClasses = ['anchor', 'perspective_shift'];
        const metaClasses = ['meta_cognitive', 'reflective_synthesis'];

        if (structureClasses.includes(questionClass)) {
            coverageStats = { ...coverageStats, structureSurfacing: coverageStats.structureSurfacing + 1 };
        } else if (mechanismClasses.includes(questionClass)) {
            coverageStats = { ...coverageStats, mechanismExploration: coverageStats.mechanismExploration + 1 };
        } else if (groundingClasses.includes(questionClass)) {
            coverageStats = { ...coverageStats, groundingPerspective: coverageStats.groundingPerspective + 1 };
        } else if (metaClasses.includes(questionClass)) {
            coverageStats = { ...coverageStats, metaLevel: coverageStats.metaLevel + 1 };
        }
    }

    function getCoveragePercentage(): number {
        const categories = [
            coverageStats.structureSurfacing > 0,
            coverageStats.mechanismExploration > 0,
            coverageStats.groundingPerspective > 0,
            coverageStats.metaLevel > 0
        ];
        return Math.round((categories.filter(Boolean).length / 4) * 100);
    }

    // Evaluate if user should consider switching thinking modes
    function evaluateModeTransition(): void {
        if (questionClassesUsed.length < 3) return; // Need pattern

        const recentClasses = questionClassesUsed.slice(-3);
        const modeCounts: Record<ThinkingMode, number> = {
            learning: 0, articulating: 0, planning: 0, ideating: 0, reflecting: 0
        };

        recentClasses.forEach(qc => {
            const suggestedModes = CLASS_TO_SUGGESTED_MODE[qc] || [];
            suggestedModes.forEach(m => modeCounts[m]++);
        });

        let maxMode: ThinkingMode | null = null;
        let maxCount = 0;
        for (const [mode, count] of Object.entries(modeCounts)) {
            if (mode !== selectedMode && count > maxCount) {
                maxCount = count;
                maxMode = mode as ThinkingMode;
            }
        }

        if (maxMode && maxCount >= 2) {
            const reasons: Record<ThinkingMode, string> = {
                learning: "Your recent questions focus on understanding mechanisms",
                articulating: "Your recent questions are about clarifying and defining",
                planning: "Your recent questions involve positioning and dimensions",
                ideating: "Your recent questions explore alternatives and perspectives",
                reflecting: "Your recent questions are about personal experience and patterns"
            };
            modeTransitionSuggestion = { targetMode: maxMode, reason: reasons[maxMode] };
        } else {
            modeTransitionSuggestion = null;
        }
    }

    // Handle mode switch from suggestion
    function handleModeSwitch(newMode: ThinkingMode): void {
        selectedMode = newMode;
        modeTransitionSuggestion = null;
        coverageStats = { structureSurfacing: 0, mechanismExploration: 0, groundingPerspective: 0, metaLevel: 0 };
        questionClassesUsed = [];
        classUsageCount = {};
        showMessage(`Switched to ${THINKING_MODES[newMode].name} mode`, 2000);
    }

    // Use response starter from hint
    function useResponseStarter(starter: string): void {
        inputText = starter;
        showQuestionHint = false;
    }

    // Use SiYuan's forwardProxy to reach backend
    async function apiPost(endpoint: string, body: any): Promise<any> {
        const url = `${backendUrl}${endpoint}`;

        const response = await fetchSyncPost('/api/network/forwardProxy', {
            url: url,
            method: 'POST',
            timeout: 30000,
            contentType: 'application/json',
            headers: [],
            payload: body
        });

        if (response.code !== 0) {
            throw new Error(`Proxy error: ${response.msg}`);
        }

        const proxyData = response.data;
        if (!proxyData) {
            throw new Error(`Proxy returned empty data`);
        }

        if (proxyData.status !== 200) {
            const errorBody = typeof proxyData.body === 'string' ? JSON.parse(proxyData.body) : proxyData.body;
            throw new Error(`Backend error ${proxyData.status}: ${JSON.stringify(errorBody)}`);
        }

        return typeof proxyData.body === 'string' ? JSON.parse(proxyData.body) : proxyData.body;
    }

    async function apiGet(endpoint: string): Promise<any> {
        const url = `${backendUrl}${endpoint}`;

        const response = await fetchSyncPost('/api/network/forwardProxy', {
            url: url,
            method: 'GET',
            timeout: 30000,
            contentType: 'application/json',
            headers: [],
        });

        if (response.code !== 0) {
            throw new Error(`Proxy error: ${response.msg}`);
        }

        const proxyData = response.data;
        if (!proxyData) {
            throw new Error(`Proxy returned empty data`);
        }

        if (proxyData.status !== 200) {
            const errorBody = typeof proxyData.body === 'string' ? JSON.parse(proxyData.body) : proxyData.body;
            throw new Error(`Backend error ${proxyData.status}: ${JSON.stringify(errorBody)}`);
        }

        return typeof proxyData.body === 'string' ? JSON.parse(proxyData.body) : proxyData.body;
    }

    // Question Engine integration
    async function detectUserState(messages: Array<{role: string, content: string}>): Promise<string> {
        try {
            // Get last few user messages for state detection
            const recentUserMessages = messages
                .filter(m => m.role === 'user')
                .slice(-3)
                .map(m => m.content);

            if (recentUserMessages.length === 0) return 'exploring';

            const data = await apiPost('/question-engine/detect-state', {
                messages: recentUserMessages,
                context: {
                    mode: selectedMode,
                    topic: sessionTopic,
                    section: template?.sections[currentSectionIndex]?.id || null
                }
            });

            return data.detected_state || 'exploring';
        } catch (err) {
            console.warn('[IES] State detection failed, using default:', err);
            return 'exploring';
        }
    }

    async function selectApproach(state: string): Promise<string> {
        try {
            // Map thinking modes to preferred approaches
            const modeApproachHints: Record<ThinkingMode, string> = {
                learning: 'socratic',
                articulating: 'phenomenological',
                planning: 'solution_focused',
                ideating: 'systems',
                reflecting: 'phenomenological'
            };

            const data = await apiPost('/question-engine/select-approach', {
                user_state: state,
                context: {
                    mode: selectedMode,
                    preferred_approach: modeApproachHints[selectedMode]
                }
            });

            return data.selected_approach || modeApproachHints[selectedMode];
        } catch (err) {
            console.warn('[IES] Approach selection failed:', err);
            return 'socratic';
        }
    }

    async function generateThinkingQuestion(
        userMessage: string,
        aiResponse: string,
        state: string,
        approach: string
    ): Promise<ClassifiedQuestion | null> {
        try {
            const data = await apiPost('/question-engine/generate-questions', {
                user_id: USER_ID,
                recent_messages: messages
                    .filter(m => m.role === 'user')
                    .slice(-3)
                    .map(m => m.content),
                context: `Mode: ${selectedMode}. Topic: ${sessionTopic}. ${
                    template?.sections[currentSectionIndex]?.prompt || ''
                }. User just said: ${userMessage}`,
                num_questions: 1
            });

            // Use classified_questions if available (new format with question class tagging)
            if (data.classified_questions && data.classified_questions.length > 0) {
                const classified = data.classified_questions[0];
                return {
                    question: classified.question,
                    question_class: classified.question_class,
                    approach: classified.approach
                };
            }

            // Fallback to old format (plain questions array)
            if (data.questions && data.questions.length > 0) {
                return {
                    question: data.questions[0],
                    question_class: 'schema_probe', // Default class
                    approach: data.approach || approach
                };
            }
            return null;
        } catch (err) {
            console.warn('[IES] Question generation failed:', err);
            return null;
        }
    }

    onMount(() => {
        const frontend = getFrontend();
        isMobile = frontend === 'mobile' || frontend === 'browser-mobile';
    });

    async function loadTemplate(templateId: string) {
        try {
            template = await apiGet(`/templates/${templateId}`);
            currentSectionIndex = 0;
            sectionResponses = {};
            showProgress = true;
        } catch (err) {
            console.warn('[IES] Template load failed, using default mode:', err);
            template = null;
            showProgress = false;
        }
    }

    async function handleStart() {
        if (!sessionTopic.trim()) {
            showMessage('Please enter a topic or question to explore', 3000, 'error');
            return;
        }

        status = 'starting';
        errorMsg = '';

        const modeConfig = THINKING_MODES[selectedMode];

        // Load template if available
        if (modeConfig.templateId) {
            await loadTemplate(modeConfig.templateId);
        }

        apiPost('/session/start', {
            user_id: USER_ID,
            mode: selectedMode,
            topic: sessionTopic,
            system_prompt: modeConfig.aiPrompt
        })
            .then(data => {
                sessionId = data.session_id;
                status = 'active';

                // Start with first section prompt if template-driven
                let greeting = data.greeting || 'What would you like to explore?';
                if (template && template.sections.length > 0) {
                    const firstSection = template.sections[0];
                    greeting = `Let's ${modeConfig.description.toLowerCase()} using the ${template.name} approach.\n\n${firstSection.prompt}`;
                } else {
                    greeting = `Let's ${modeConfig.description.toLowerCase()}. ${greeting}`;
                }

                messages = [{
                    role: 'assistant',
                    content: greeting
                }];
            })
            .catch(err => {
                console.error('[IES] Start error:', err);
                status = 'error';
                errorMsg = err.message || String(err);
                showMessage(`Error: ${errorMsg}`, 5000, 'error');
            });
    }

    function handleSend() {
        if (!inputText.trim() || isLoading || !sessionId) return;

        const userMsg = inputText.trim();
        inputText = '';
        messages = [...messages, { role: 'user', content: userMsg }];
        messages = [...messages, { role: 'assistant', content: '...' }];
        isLoading = true;

        // Store section response if template-driven
        if (template && currentSectionIndex < template.sections.length) {
            const section = template.sections[currentSectionIndex];
            sectionResponses[section.id] = userMsg;
        }

        const modeConfig = THINKING_MODES[selectedMode];

        // Build enhanced prompt with section context
        let enhancedPrompt = userMsg;
        if (template && currentSectionIndex < template.sections.length) {
            const section = template.sections[currentSectionIndex];
            if (section.ai_behavior) {
                enhancedPrompt = `${section.ai_behavior}\n\nUser response: ${userMsg}`;
            }
        }

        apiPost('/session/chat-sync', {
            session_id: sessionId,
            message: enhancedPrompt,
            messages: messages.slice(0, -1),
            mode: selectedMode,
            mode_prompt: modeConfig.aiPrompt
        })
            .then(async data => {
                let response = data.response || '';

                // Advance to next section if template-driven
                if (template && currentSectionIndex < template.sections.length - 1) {
                    currentSectionIndex++;
                    const nextSection = template.sections[currentSectionIndex];

                    // Detect state and potentially add a thinking question before next section
                    detectedState = await detectUserState(messages);
                    currentApproach = await selectApproach(detectedState);

                    // Generate thinking question if user seems stuck or overwhelmed
                    if (detectedState === 'stuck' || detectedState === 'overwhelmed' || detectedState === 'uncertain') {
                        const classifiedQuestion = await generateThinkingQuestion(
                            userMsg,
                            response,
                            detectedState,
                            currentApproach
                        );
                        if (classifiedQuestion) {
                            // Track the question class used
                            lastQuestionClass = classifiedQuestion.question_class;
                            if (!questionClassesUsed.includes(classifiedQuestion.question_class)) {
                                questionClassesUsed = [...questionClassesUsed, classifiedQuestion.question_class];
                            }
                            // Track usage count and update coverage stats
                            classUsageCount[classifiedQuestion.question_class] =
                                (classUsageCount[classifiedQuestion.question_class] || 0) + 1;
                            updateCoverageStats(classifiedQuestion.question_class);
                            evaluateModeTransition();
                            showQuestionHint = true;

                            // Set as pending question for INTERACTIVE response (not passive display)
                            pendingQuestion = {
                                question: classifiedQuestion.question,
                                questionClass: classifiedQuestion.question_class,
                                approach: classifiedQuestion.approach,
                                generatedAt: Date.now()
                            };
                        }
                    }

                    response += `\n\n${nextSection.prompt}`;
                } else if (!template) {
                    // Use question engine for non-template sessions
                    // Detect user state from conversation
                    detectedState = await detectUserState(messages);

                    // Select appropriate questioning approach
                    currentApproach = await selectApproach(detectedState);

                    // Generate a thinking partner question
                    const classifiedQuestion = await generateThinkingQuestion(
                        userMsg,
                        response,
                        detectedState,
                        currentApproach
                    );

                    if (classifiedQuestion) {
                        // Track the question class used
                        lastQuestionClass = classifiedQuestion.question_class;
                        if (!questionClassesUsed.includes(classifiedQuestion.question_class)) {
                            questionClassesUsed = [...questionClassesUsed, classifiedQuestion.question_class];
                        }
                        // Track usage count and update coverage stats
                        classUsageCount[classifiedQuestion.question_class] =
                            (classUsageCount[classifiedQuestion.question_class] || 0) + 1;
                        updateCoverageStats(classifiedQuestion.question_class);
                        evaluateModeTransition();
                        showQuestionHint = true;

                        // Set as pending question for INTERACTIVE response (not passive display)
                        pendingQuestion = {
                            question: classifiedQuestion.question,
                            questionClass: classifiedQuestion.question_class,
                            approach: classifiedQuestion.approach,
                            generatedAt: Date.now()
                        };
                    }
                }

                messages[messages.length - 1].content = response;
                messages = messages;
                isLoading = false;
            })
            .catch(err => {
                console.error('[IES] Chat error:', err);
                messages = messages.slice(0, -1);
                showMessage(`Chat error: ${err.message}`, 5000, 'error');
                isLoading = false;
            });
    }

    async function handleEnd() {
        if (!sessionId) return;
        status = 'starting';

        const endPayload: any = {
            session_id: sessionId,
            user_id: USER_ID,
            transcript: messages
        };

        // Add template data if available
        if (template) {
            endPayload.template_id = template.id;
            endPayload.section_responses = sectionResponses;
        }

        try {
            const data = await apiPost('/session/end', endPayload);

            // Create session document in SiYuan
            const docId = await createSessionDocument({
                sessionId: sessionId,
                mode: selectedMode,
                topic: sessionTopic,
                templateId: template?.id,
                templateName: template?.name,
                sectionResponses: template ? sectionResponses : undefined,
                transcript: messages,
                entitiesExtracted: data.entities_extracted,
                graphMappingExecuted: !!template,
                questionClassesUsed: questionClassesUsed.length > 0 ? questionClassesUsed : undefined,
                questionResponseHistory: questionResponseHistory.length > 0 ? questionResponseHistory : undefined,
            });

            const docMsg = docId ? ' Session document saved to SiYuan.' : '';
            const dialogueMsg = questionResponseHistory.length > 0
                ? ` ${questionResponseHistory.length} thinking dialogue${questionResponseHistory.length > 1 ? 's' : ''} captured.`
                : '';
            const classesMsg = questionClassesUsed.length > 0
                ? ` Question types: ${questionClassesUsed.map(c => QUESTION_CLASS_LABELS[c]?.label || c).join(', ')}.`
                : '';
            const msg = template
                ? `Session saved. Template mapping executed. ${data.entities_extracted} entities extracted.${dialogueMsg}${classesMsg}${docMsg}`
                : `Session saved. ${data.entities_extracted} entities extracted.${dialogueMsg}${classesMsg}${docMsg}`;
            showMessage(msg, 4000);

            // Reset state
            sessionId = null;
            status = 'idle';
            messages = [];
            template = null;
            sectionResponses = {};
            currentSectionIndex = 0;
            showProgress = false;
            questionClassesUsed = [];
            lastQuestionClass = null;
            pendingQuestion = null;
            questionResponseText = '';
            questionResponseHistory = [];
            classUsageCount = {};
            coverageStats = { structureSurfacing: 0, mechanismExploration: 0, groundingPerspective: 0, metaLevel: 0 };
            modeTransitionSuggestion = null;
        } catch (err) {
            console.error('[IES] End error:', err);
            status = 'error';
            errorMsg = err.message;
            showMessage(`Error: ${err.message}`, 5000, 'error');
        }
    }

    function handleKeydown(e: KeyboardEvent) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    }

    function handleQuestionKeydown(e: KeyboardEvent) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleQuestionResponse();
        }
    }

    /**
     * Handle user's response to a thinking partner question.
     * This creates an actual dialogue loop:
     * 1. Record the question-response pair
     * 2. Detect user's new cognitive state from their response
     * 3. Generate a contextual follow-up question
     * 4. Update coverage tracking
     */
    async function handleQuestionResponse() {
        if (!pendingQuestion || !questionResponseText.trim() || isProcessingQuestion) return;

        isProcessingQuestion = true;
        const response = questionResponseText.trim();
        const currentQuestion = pendingQuestion;
        questionResponseText = '';

        try {
            // Add the question-response exchange to messages for full transcript
            messages = [...messages, {
                role: 'assistant',
                content: `💭 *Thinking Question (${QUESTION_CLASS_LABELS[currentQuestion.questionClass]?.label || 'Thinking'}):* ${currentQuestion.question}`
            }, {
                role: 'user',
                content: response
            }];

            // Detect new cognitive state based on the response
            const newState = await detectUserState(messages);
            detectedState = newState;

            // Select approach that fits the new state
            const newApproach = await selectApproach(newState);
            currentApproach = newApproach;

            // Generate follow-up question based on the response
            const followUp = await generateThinkingQuestion(
                response,
                '', // No separate AI response - this IS the thinking dialogue
                newState,
                newApproach
            );

            // Record the Q&A pair in history
            questionResponseHistory = [...questionResponseHistory, {
                question: currentQuestion.question,
                questionClass: currentQuestion.questionClass,
                userResponse: response,
                followUpQuestion: followUp?.question,
                timestamp: Date.now()
            }];

            // Update pending question with follow-up (or clear if none)
            if (followUp) {
                pendingQuestion = {
                    question: followUp.question,
                    questionClass: followUp.question_class,
                    approach: followUp.approach,
                    generatedAt: Date.now()
                };

                // Track the new question class
                lastQuestionClass = followUp.question_class;
                if (!questionClassesUsed.includes(followUp.question_class)) {
                    questionClassesUsed = [...questionClassesUsed, followUp.question_class];
                }
                classUsageCount[followUp.question_class] =
                    (classUsageCount[followUp.question_class] || 0) + 1;
                updateCoverageStats(followUp.question_class);
                evaluateModeTransition();
                showQuestionHint = true;
            } else {
                // No follow-up generated - thinking dialogue complete for now
                pendingQuestion = null;
                showQuestionHint = false;
            }
        } catch (err) {
            console.error('[IES] Question response error:', err);
            showMessage('Error processing your response. Please try again.', 3000, 'error');
            // Restore the question so user can retry
            pendingQuestion = currentQuestion;
        } finally {
            isProcessingQuestion = false;
        }
    }

    /**
     * Skip the current thinking question without responding.
     * User can continue the main conversation instead.
     */
    function skipQuestion() {
        if (pendingQuestion) {
            // Record that this question was skipped (for analytics)
            questionResponseHistory = [...questionResponseHistory, {
                question: pendingQuestion.question,
                questionClass: pendingQuestion.questionClass,
                userResponse: '[skipped]',
                timestamp: Date.now()
            }];
        }
        pendingQuestion = null;
        showQuestionHint = false;
    }

    function handleBack() {
        dispatch('back');
    }

    // Helper to get section completion status
    function getSectionStatus(sectionId: string, index: number): 'complete' | 'current' | 'pending' {
        if (sectionId in sectionResponses) return 'complete';
        if (index === currentSectionIndex) return 'current';
        return 'pending';
    }
</script>

<div class="forge-mode" class:forge-mode--split={showProgress && status === 'active'}>
    <div class="forge-header">
        <button class="back-btn" on:click={handleBack} title="Back to Dashboard">
            <svg viewBox="0 0 24 24" width="16" height="16">
                <path fill="currentColor" d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
            </svg>
        </button>
        <span class="forge-title">Structured Thinking</span>
        {#if status === 'active'}
            <span class="forge-badge">{THINKING_MODES[selectedMode].icon} {THINKING_MODES[selectedMode].name}</span>
            {#if template}
                <span class="template-badge">{template.name}</span>
            {/if}
        {/if}
    </div>

    <div class="forge-main">
        <div class="forge-conversation">
            {#if status === 'idle'}
                <!-- Mode Selection -->
                <div class="forge-setup">
                    <div class="setup-section">
                        <label class="setup-label">Thinking Mode</label>
                        <div class="mode-selector">
                            {#each Object.entries(THINKING_MODES) as [key, mode]}
                                <button
                                    class="mode-option"
                                    class:mode-option--selected={selectedMode === key}
                                    on:click={() => selectedMode = key}
                                >
                                    <span class="mode-option-icon">{mode.icon}</span>
                                    <span class="mode-option-name">{mode.name}</span>
                                    <span class="mode-option-desc">{mode.description}</span>
                                    {#if mode.templateId}
                                        <span class="template-indicator" title="Template-driven session">⚙️</span>
                                    {/if}
                                </button>
                            {/each}
                        </div>
                    </div>

                    <div class="setup-section">
                        <label class="setup-label">What do you want to explore?</label>
                        <textarea
                            class="topic-input"
                            bind:value={sessionTopic}
                            placeholder="Enter your topic, question, or idea..."
                            rows="2"
                        ></textarea>
                    </div>

                    <button
                        class="b3-button b3-button--primary start-btn"
                        on:click={handleStart}
                        disabled={!sessionTopic.trim()}
                    >
                        Start {THINKING_MODES[selectedMode].name} Session
                    </button>
                </div>

            {:else if status === 'starting'}
                <div class="forge-loading">Starting {THINKING_MODES[selectedMode].name} session...</div>

            {:else if status === 'error'}
                <div class="forge-error">{errorMsg}</div>
                <button class="b3-button" on:click={() => status = 'idle'}>Try Again</button>

            {:else}
                <!-- Active Session -->
                <div class="forge-messages">
                    {#each messages as msg}
                        <div class="forge-msg" class:forge-msg--user={msg.role === 'user'}>
                            {msg.content}
                        </div>
                    {/each}
                </div>

                <!-- Interactive Thinking Question Card -->
                {#if pendingQuestion}
                    {@const classInfo = QUESTION_CLASS_LABELS[pendingQuestion.questionClass]}
                    {@const hintInfo = QUESTION_CLASS_HINTS[pendingQuestion.questionClass]}
                    <div class="question-response-card" style="--class-color: {classInfo?.color || '#888'}">
                        <div class="qrc-header">
                            <span class="qrc-icon">{classInfo?.emoji || '💭'}</span>
                            <span class="qrc-label">{classInfo?.label || 'Thinking'} Question</span>
                            <span class="qrc-badge">Thinking Partner</span>
                        </div>

                        <div class="qrc-question">
                            {pendingQuestion.question}
                        </div>

                        <!-- Cognitive Guidance Hint -->
                        {#if hintInfo}
                            <div class="qrc-hint">
                                <p class="qrc-hint-text">{hintInfo.hint}</p>
                                <p class="qrc-hint-prompt"><strong>Try:</strong> {hintInfo.prompt}</p>
                            </div>
                        {/if}

                        <textarea
                            class="qrc-input"
                            bind:value={questionResponseText}
                            on:keydown={handleQuestionKeydown}
                            placeholder="Your response to this thinking question..."
                            rows="3"
                            disabled={isProcessingQuestion}
                        ></textarea>

                        <div class="qrc-actions">
                            {#if hintInfo?.responseStarter}
                                <button
                                    class="qrc-starter"
                                    on:click={() => questionResponseText = hintInfo.responseStarter}
                                    disabled={isProcessingQuestion}
                                >
                                    Start with: "{hintInfo.responseStarter}"
                                </button>
                            {/if}
                            <div class="qrc-buttons">
                                <button
                                    class="qrc-skip"
                                    on:click={skipQuestion}
                                    disabled={isProcessingQuestion}
                                >
                                    Skip
                                </button>
                                <button
                                    class="qrc-respond"
                                    on:click={handleQuestionResponse}
                                    disabled={isProcessingQuestion || !questionResponseText.trim()}
                                >
                                    {isProcessingQuestion ? 'Processing...' : 'Respond'}
                                </button>
                            </div>
                        </div>

                        <!-- Question-Response History Summary -->
                        {#if questionResponseHistory.length > 0}
                            <div class="qrc-history">
                                <span class="qrc-history-label">{questionResponseHistory.length} thinking exchange{questionResponseHistory.length > 1 ? 's' : ''} this session</span>
                            </div>
                        {/if}
                    </div>
                {/if}

                <div class="forge-input">
                    <textarea
                        bind:value={inputText}
                        on:keydown={handleKeydown}
                        placeholder="Type your response..."
                        rows="2"
                        disabled={isLoading}
                    ></textarea>
                    <div class="forge-actions">
                        <button
                            class="b3-button b3-button--primary"
                            on:click={handleSend}
                            disabled={isLoading || !inputText.trim()}
                        >
                            {isLoading ? '...' : 'Send'}
                        </button>
                        <button class="b3-button" on:click={handleEnd}>
                            End
                        </button>
                    </div>
                    {#if questionClassesUsed.length > 0}
                        <div class="question-classes-bar">
                            <span class="question-classes-label">Questions used:</span>
                            <div class="question-class-badges">
                                {#each questionClassesUsed as qc}
                                    {@const classInfo = QUESTION_CLASS_LABELS[qc]}
                                    {#if classInfo}
                                        <span
                                            class="question-class-badge"
                                            class:question-class-badge--active={lastQuestionClass === qc}
                                            style="--badge-color: {classInfo.color}"
                                            title={qc.replace(/_/g, ' ')}
                                        >
                                            {classInfo.emoji} {classInfo.label}
                                        </span>
                                    {/if}
                                {/each}
                            </div>
                        </div>
                    {/if}

                    <!-- Question Hint Panel - Active Cognitive Guidance -->
                    {#if lastQuestionClass && showQuestionHint}
                        {@const hintInfo = QUESTION_CLASS_HINTS[lastQuestionClass]}
                        {@const classInfo = QUESTION_CLASS_LABELS[lastQuestionClass]}
                        <div class="question-hint-panel" class:question-hint-panel--expanded={questionHintExpanded} style="--class-color: {classInfo?.color || '#888'}">
                            <button class="question-hint-header" on:click={() => questionHintExpanded = !questionHintExpanded}>
                                <span class="question-hint-icon">{classInfo?.emoji || '💭'}</span>
                                <span class="question-hint-type">{classInfo?.label || 'Thinking'} Question</span>
                                <span class="question-hint-toggle">{questionHintExpanded ? '▼' : '▶'}</span>
                            </button>

                            {#if questionHintExpanded}
                                <div class="question-hint-content">
                                    <p class="question-hint-text">{hintInfo?.hint}</p>
                                    <p class="question-hint-prompt"><strong>Try this:</strong> {hintInfo?.prompt}</p>
                                    {#if hintInfo?.responseStarter}
                                        <button class="question-hint-starter" on:click={() => useResponseStarter(hintInfo.responseStarter)}>
                                            Start with: "{hintInfo.responseStarter}"
                                        </button>
                                    {/if}
                                </div>
                            {/if}

                            <button class="question-hint-dismiss" on:click|stopPropagation={() => showQuestionHint = false} title="Dismiss hint">&times;</button>
                        </div>
                    {/if}

                    <!-- Mode Transition Suggestion -->
                    {#if modeTransitionSuggestion}
                        <div class="mode-transition-suggestion">
                            <div class="suggestion-content">
                                <span class="suggestion-icon">{THINKING_MODES[modeTransitionSuggestion.targetMode].icon}</span>
                                <div class="suggestion-text">
                                    <span class="suggestion-label">Consider switching to {THINKING_MODES[modeTransitionSuggestion.targetMode].name}</span>
                                    <span class="suggestion-reason">{modeTransitionSuggestion.reason}</span>
                                </div>
                            </div>
                            <div class="suggestion-actions">
                                <button class="suggestion-accept" on:click={() => handleModeSwitch(modeTransitionSuggestion.targetMode)}>
                                    Switch Mode
                                </button>
                                <button class="suggestion-dismiss" on:click={() => modeTransitionSuggestion = null}>
                                    Stay Here
                                </button>
                            </div>
                        </div>
                    {/if}

                    <!-- Cognitive Coverage Indicator -->
                    {#if questionClassesUsed.length > 0}
                        <div class="cognitive-coverage">
                            <div class="coverage-header">
                                <span class="coverage-label">Thinking Coverage</span>
                                <span class="coverage-percent">{getCoveragePercentage()}%</span>
                            </div>
                            <div class="coverage-bars">
                                <div class="coverage-bar" class:coverage-bar--active={coverageStats.structureSurfacing > 0}>
                                    <span class="bar-icon">🏗️</span>
                                    <span class="bar-label">Structure</span>
                                    <span class="bar-count">{coverageStats.structureSurfacing}</span>
                                </div>
                                <div class="coverage-bar" class:coverage-bar--active={coverageStats.mechanismExploration > 0}>
                                    <span class="bar-icon">⚡</span>
                                    <span class="bar-label">Mechanism</span>
                                    <span class="bar-count">{coverageStats.mechanismExploration}</span>
                                </div>
                                <div class="coverage-bar" class:coverage-bar--active={coverageStats.groundingPerspective > 0}>
                                    <span class="bar-icon">⚓</span>
                                    <span class="bar-label">Grounding</span>
                                    <span class="bar-count">{coverageStats.groundingPerspective}</span>
                                </div>
                                <div class="coverage-bar" class:coverage-bar--active={coverageStats.metaLevel > 0}>
                                    <span class="bar-icon">🧠</span>
                                    <span class="bar-label">Meta</span>
                                    <span class="bar-count">{coverageStats.metaLevel}</span>
                                </div>
                            </div>
                        </div>
                    {/if}
                </div>
            {/if}
        </div>

        {#if showProgress && template && status === 'active'}
            <div class="forge-progress">
                <div class="progress-header">
                    <span class="progress-title">{template.name}</span>
                    <span class="progress-count">{Object.keys(sectionResponses).length}/{template.sections.length}</span>
                </div>
                <div class="progress-sections">
                    {#each template.sections as section, index}
                        {@const sectionStatus = getSectionStatus(section.id, index)}
                        <div class="progress-section" class:progress-section--complete={sectionStatus === 'complete'} class:progress-section--current={sectionStatus === 'current'}>
                            <div class="progress-section-header">
                                <span class="progress-section-icon">
                                    {#if sectionStatus === 'complete'}✓
                                    {:else if sectionStatus === 'current'}▶
                                    {:else}○
                                    {/if}
                                </span>
                                <span class="progress-section-label">{section.prompt}</span>
                            </div>
                            {#if section.id in sectionResponses}
                                <div class="progress-section-response">
                                    {sectionResponses[section.id]}
                                </div>
                            {/if}
                        </div>
                    {/each}
                </div>
                {#if template.graph_mapping && template.graph_mapping.on_complete}
                    <div class="progress-footer">
                        <span class="progress-footer-label">On completion:</span>
                        <ul class="progress-actions">
                            {#each template.graph_mapping.on_complete as action}
                                <li class="progress-action">
                                    {#if action.action === 'create_or_link'}
                                        Create {action.entity_type || 'spark'} entity
                                    {:else if action.action === 'update_journey'}
                                        Update journey
                                    {:else}
                                        {action.action}
                                    {/if}
                                </li>
                            {/each}
                        </ul>
                    </div>
                {/if}
            </div>
        {/if}
    </div>
</div>

<style>
    /* Design tokens - matches Dashboard.svelte */
    .forge-mode {
        --font-display: 'Crimson Pro', Georgia, serif;
        --font-body: 'Nunito', system-ui, sans-serif;
        --font-mono: 'JetBrains Mono', monospace;

        --space-1: 0.25rem;
        --space-2: 0.5rem;
        --space-3: 0.75rem;
        --space-4: 1rem;
        --space-5: 1.25rem;
        --space-6: 1.5rem;

        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-full: 9999px;

        /* Light theme (default) */
        --bg-deep: #f7f5f2;
        --bg-base: #fffefa;
        --bg-elevated: #ffffff;
        --bg-overlay: rgba(255, 254, 250, 0.95);

        --text-primary: #1a1816;
        --text-secondary: #4a4641;
        --text-muted: #7a756e;
        --text-subtle: #a9a29a;

        --border-subtle: rgba(26, 24, 22, 0.06);
        --border-light: rgba(26, 24, 22, 0.1);
        --border-medium: rgba(26, 24, 22, 0.15);

        --accent: #c98b2f;
        --accent-light: #f5ddb8;
        --accent-lighter: #fdf4e6;
        --accent-dark: #9a6820;

        --secondary: #5a8a7a;
        --secondary-light: #c4ddd5;
        --secondary-lighter: #eef5f3;

        --tertiary: #8b7aa0;
        --tertiary-light: #ddd6e8;

        --shadow-sm: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.06);
        --shadow-md: 0 4px 12px rgba(0,0,0,0.06), 0 2px 4px rgba(0,0,0,0.04);
        --shadow-lg: 0 8px 24px rgba(0,0,0,0.08), 0 4px 8px rgba(0,0,0,0.04);

        display: flex;
        flex-direction: column;
        height: 100%;
        padding: var(--space-3);
        gap: var(--space-3);
        font-family: var(--font-body);
        color: var(--text-primary);
        background: var(--bg-deep);
    }

    /* Dark theme support */
    :global([data-theme-mode="dark"]) .forge-mode {
        --bg-deep: #141312;
        --bg-base: #1c1a18;
        --bg-elevated: #242220;
        --bg-overlay: rgba(28, 26, 24, 0.95);

        --text-primary: #f4f2ef;
        --text-secondary: #c9c5bf;
        --text-muted: #8a857e;
        --text-subtle: #5a5650;

        --border-subtle: rgba(244, 242, 239, 0.04);
        --border-light: rgba(244, 242, 239, 0.08);
        --border-medium: rgba(244, 242, 239, 0.12);

        --accent-light: #4a3a20;
        --accent-lighter: #2a2218;

        --secondary-light: #2a3a35;
        --secondary-lighter: #1a2522;

        --shadow-sm: 0 1px 3px rgba(0,0,0,0.2);
        --shadow-md: 0 4px 12px rgba(0,0,0,0.25);
        --shadow-lg: 0 8px 24px rgba(0,0,0,0.3);
    }

    .forge-header {
        display: flex;
        align-items: center;
        gap: var(--space-2);
    }
    .back-btn {
        background: none;
        border: none;
        cursor: pointer;
        padding: 4px;
        border-radius: var(--radius-sm);
        color: var(--text-secondary);
        display: flex;
        align-items: center;
        transition: all 0.15s ease;
    }
    .back-btn:hover {
        background: var(--bg-elevated);
        color: var(--text-primary);
    }
    .forge-title {
        font-family: var(--font-display);
        font-weight: 600;
        flex: 1;
        color: var(--text-primary);
    }
    .forge-badge {
        font-size: 12px;
        padding: 2px 8px;
        background: var(--accent-lighter);
        color: var(--accent);
        border-radius: var(--radius-sm);
    }
    .template-badge {
        font-size: 11px;
        padding: 2px 6px;
        background: var(--secondary-lighter);
        color: var(--secondary);
        border-radius: var(--radius-sm);
    }

    /* Main layout - conversation and progress side by side */
    .forge-main {
        flex: 1;
        display: flex;
        gap: var(--space-3);
        overflow: hidden;
    }
    .forge-conversation {
        flex: 1;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }
    .forge-mode--split .forge-conversation {
        flex: 1;
    }

    /* Progress panel */
    .forge-progress {
        width: 300px;
        display: flex;
        flex-direction: column;
        border: 1px solid var(--border-light);
        border-radius: var(--radius-md);
        overflow: hidden;
        background: var(--bg-base);
        box-shadow: var(--shadow-sm);
    }
    .progress-header {
        padding: var(--space-3);
        background: var(--bg-elevated);
        border-bottom: 1px solid var(--border-subtle);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .progress-title {
        font-size: 12px;
        font-weight: 600;
        color: var(--text-primary);
        font-family: var(--font-display);
    }
    .progress-count {
        font-size: 11px;
        padding: 2px 6px;
        background: var(--accent-lighter);
        color: var(--accent);
        border-radius: var(--radius-sm);
    }
    .progress-sections {
        flex: 1;
        overflow-y: auto;
        padding: var(--space-2);
    }
    .progress-section {
        margin-bottom: var(--space-3);
        padding: var(--space-2);
        border-radius: var(--radius-sm);
        background: var(--bg-elevated);
        border: 1px solid var(--border-subtle);
        transition: all 0.15s ease;
    }
    .progress-section--current {
        border-color: var(--accent);
        background: var(--accent-lighter);
    }
    .progress-section--complete {
        opacity: 0.7;
    }
    .progress-section-header {
        display: flex;
        gap: 6px;
        align-items: flex-start;
    }
    .progress-section-icon {
        font-size: 12px;
        margin-top: 1px;
    }
    .progress-section-label {
        flex: 1;
        font-size: 12px;
        line-height: 1.4;
        color: var(--text-primary);
    }
    .progress-section-response {
        margin-top: 6px;
        padding-top: 6px;
        border-top: 1px solid var(--border-subtle);
        font-size: 11px;
        color: var(--text-muted);
        white-space: pre-wrap;
        max-height: 60px;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .progress-footer {
        padding: var(--space-2) var(--space-3);
        border-top: 1px solid var(--border-subtle);
        background: var(--bg-elevated);
    }
    .progress-footer-label {
        font-size: 10px;
        font-weight: 600;
        text-transform: uppercase;
        color: var(--text-muted);
        letter-spacing: 0.05em;
    }
    .progress-actions {
        margin: 4px 0 0 0;
        padding: 0 0 0 16px;
        list-style: disc;
    }
    .progress-action {
        font-size: 11px;
        color: var(--text-secondary);
        margin: 2px 0;
    }

    /* Setup section (mode selection + topic) */
    .forge-setup {
        display: flex;
        flex-direction: column;
        gap: var(--space-4);
        padding: var(--space-3) 0;
    }
    .setup-section {
        display: flex;
        flex-direction: column;
        gap: var(--space-2);
    }
    .setup-label {
        font-size: 12px;
        font-weight: 600;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-family: var(--font-display);
    }

    /* Mode selector */
    .mode-selector {
        display: flex;
        flex-direction: column;
        gap: 6px;
    }
    .mode-option {
        display: flex;
        align-items: center;
        gap: var(--space-3);
        padding: var(--space-3);
        background: var(--bg-elevated);
        border: 2px solid var(--border-light);
        border-radius: var(--radius-md);
        cursor: pointer;
        transition: all 0.15s ease;
        text-align: left;
    }
    .mode-option:hover {
        border-color: var(--accent-light);
        background: var(--accent-lighter);
        box-shadow: var(--shadow-sm);
    }
    .mode-option--selected {
        border-color: var(--accent);
        background: var(--accent-lighter);
        box-shadow: var(--shadow-sm);
    }
    .mode-option-icon {
        font-size: 18px;
    }
    .mode-option-name {
        font-weight: 600;
        font-size: 13px;
        min-width: 80px;
        color: var(--text-primary);
    }
    .mode-option-desc {
        flex: 1;
        font-size: 12px;
        color: var(--text-muted);
    }
    .template-indicator {
        font-size: 12px;
        opacity: 0.6;
    }

    /* Topic input */
    .topic-input {
        width: 100%;
        resize: none;
        border: 1px solid var(--border-light);
        border-radius: var(--radius-md);
        padding: var(--space-3);
        font-size: 14px;
        background: var(--bg-elevated);
        color: var(--text-primary);
        font-family: var(--font-body);
        transition: all 0.15s ease;
    }
    .topic-input:focus {
        outline: none;
        border-color: var(--accent);
        box-shadow: 0 0 0 3px var(--accent-lighter);
    }
    .topic-input::placeholder {
        color: var(--text-subtle);
    }
    .start-btn {
        align-self: flex-start;
        padding: var(--space-3) var(--space-5);
        background: var(--accent);
        color: white;
        border: none;
        border-radius: var(--radius-sm);
        font-weight: 600;
        cursor: pointer;
        transition: all 0.15s ease;
    }
    .start-btn:hover {
        background: var(--accent-dark);
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }

    /* Loading and error states */
    .forge-loading {
        text-align: center;
        color: var(--text-muted);
        padding: var(--space-6);
    }
    .forge-error {
        color: #dc2626;
        font-size: 13px;
        padding: var(--space-3);
        text-align: center;
        background: rgba(220, 38, 38, 0.1);
        border-radius: var(--radius-sm);
    }

    /* Messages */
    .forge-messages {
        flex: 1;
        overflow-y: auto;
        padding-bottom: var(--space-3);
    }
    .forge-msg {
        padding: var(--space-3);
        margin-bottom: var(--space-2);
        border-radius: var(--radius-md);
        background: var(--bg-elevated);
        font-size: 14px;
        line-height: 1.6;
        white-space: pre-wrap;
        border: 1px solid var(--border-subtle);
    }
    .forge-msg--user {
        background: var(--accent-lighter);
        border-color: var(--accent-light);
        margin-left: 20px;
    }

    /* Input area */
    .forge-input {
        display: flex;
        flex-direction: column;
        gap: var(--space-2);
        padding-top: var(--space-3);
        border-top: 1px solid var(--border-light);
    }
    .forge-input textarea {
        width: 100%;
        resize: none;
        border: 1px solid var(--border-light);
        border-radius: var(--radius-sm);
        padding: var(--space-2);
        font-size: 14px;
        background: var(--bg-elevated);
        color: var(--text-primary);
        font-family: var(--font-body);
        transition: all 0.15s ease;
    }
    .forge-input textarea:focus {
        outline: none;
        border-color: var(--accent);
        box-shadow: 0 0 0 3px var(--accent-lighter);
    }
    .forge-actions {
        display: flex;
        gap: var(--space-2);
        justify-content: flex-end;
    }

    /* Question class badges */
    .question-classes-bar {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        padding: var(--space-2) 0;
        flex-wrap: wrap;
    }
    .question-classes-label {
        font-size: 11px;
        color: var(--text-muted);
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.05em;
    }
    .question-class-badges {
        display: flex;
        gap: 6px;
        flex-wrap: wrap;
    }
    .question-class-badge {
        display: inline-flex;
        align-items: center;
        gap: 3px;
        padding: 2px 8px;
        font-size: 11px;
        border-radius: var(--radius-full);
        background: color-mix(in srgb, var(--badge-color, #888) 15%, transparent);
        color: var(--badge-color, #888);
        border: 1px solid color-mix(in srgb, var(--badge-color, #888) 30%, transparent);
        transition: all 0.15s ease;
    }
    .question-class-badge--active {
        background: color-mix(in srgb, var(--badge-color, #888) 25%, transparent);
        border-color: var(--badge-color, #888);
        box-shadow: 0 0 6px color-mix(in srgb, var(--badge-color, #888) 40%, transparent);
    }

    /* Question Hint Panel - Active Cognitive Guidance */
    .question-hint-panel {
        background: color-mix(in srgb, var(--class-color, #888) 8%, var(--bg-base));
        border: 1px solid color-mix(in srgb, var(--class-color, #888) 25%, var(--border-light));
        border-radius: var(--radius-md);
        margin: var(--space-2) 0;
        position: relative;
        overflow: hidden;
        transition: all 0.2s ease;
    }
    .question-hint-panel:hover {
        border-color: color-mix(in srgb, var(--class-color, #888) 40%, var(--border-light));
    }
    .question-hint-header {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        padding: var(--space-3);
        width: 100%;
        background: none;
        border: none;
        cursor: pointer;
        text-align: left;
        color: var(--text-primary);
    }
    .question-hint-icon {
        font-size: 16px;
    }
    .question-hint-type {
        flex: 1;
        font-size: 13px;
        font-weight: 500;
        color: var(--class-color, #888);
    }
    .question-hint-toggle {
        font-size: 10px;
        color: var(--text-muted);
        transition: transform 0.15s ease;
    }
    .question-hint-panel--expanded .question-hint-toggle {
        transform: rotate(90deg);
    }
    .question-hint-content {
        padding: 0 var(--space-3) var(--space-3);
        border-top: 1px solid color-mix(in srgb, var(--class-color, #888) 15%, var(--border-subtle));
        margin-top: 0;
    }
    .question-hint-text {
        font-size: 12px;
        color: var(--text-secondary);
        margin: var(--space-3) 0 var(--space-2);
        line-height: 1.5;
    }
    .question-hint-prompt {
        font-size: 12px;
        color: var(--text-muted);
        margin: 0 0 var(--space-3);
        padding: var(--space-2);
        background: var(--bg-elevated);
        border-radius: var(--radius-sm);
    }
    .question-hint-starter {
        font-size: 11px;
        padding: 6px var(--space-3);
        background: color-mix(in srgb, var(--class-color, #888) 15%, var(--bg-base));
        color: var(--class-color, #888);
        border: 1px solid color-mix(in srgb, var(--class-color, #888) 30%, transparent);
        border-radius: var(--radius-sm);
        cursor: pointer;
        transition: all 0.15s ease;
    }
    .question-hint-starter:hover {
        background: color-mix(in srgb, var(--class-color, #888) 25%, var(--bg-base));
        border-color: var(--class-color, #888);
    }
    .question-hint-dismiss {
        position: absolute;
        top: 6px;
        right: 6px;
        width: 20px;
        height: 20px;
        background: none;
        border: none;
        font-size: 14px;
        color: var(--text-muted);
        cursor: pointer;
        border-radius: 3px;
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0.6;
        transition: opacity 0.15s ease;
    }
    .question-hint-dismiss:hover {
        opacity: 1;
        background: var(--bg-elevated);
    }

    /* Mode Transition Suggestion */
    .mode-transition-suggestion {
        background: linear-gradient(135deg,
            color-mix(in srgb, var(--accent) 10%, var(--bg-base)),
            color-mix(in srgb, var(--secondary) 10%, var(--bg-base))
        );
        border: 1px solid var(--accent-light);
        border-radius: var(--radius-md);
        padding: var(--space-3);
        margin: var(--space-3) 0;
        animation: pulse-soft 2s ease-in-out infinite;
    }
    @keyframes pulse-soft {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.92; }
    }
    .suggestion-content {
        display: flex;
        align-items: flex-start;
        gap: var(--space-3);
        margin-bottom: var(--space-3);
    }
    .suggestion-icon {
        font-size: 24px;
        line-height: 1;
    }
    .suggestion-text {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 2px;
    }
    .suggestion-label {
        font-size: 13px;
        font-weight: 600;
        color: var(--text-primary);
    }
    .suggestion-reason {
        font-size: 11px;
        color: var(--text-muted);
        line-height: 1.4;
    }
    .suggestion-actions {
        display: flex;
        gap: var(--space-2);
        justify-content: flex-end;
    }
    .suggestion-accept {
        font-size: 12px;
        padding: 6px 14px;
        background: var(--accent);
        color: white;
        border: none;
        border-radius: var(--radius-sm);
        cursor: pointer;
        font-weight: 500;
        transition: all 0.15s ease;
    }
    .suggestion-accept:hover {
        background: var(--accent-dark);
        transform: translateY(-1px);
    }
    .suggestion-dismiss {
        font-size: 12px;
        padding: 6px 14px;
        background: var(--bg-elevated);
        color: var(--text-secondary);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-sm);
        cursor: pointer;
        transition: all 0.15s ease;
    }
    .suggestion-dismiss:hover {
        background: var(--bg-base);
    }

    /* Cognitive Coverage Indicator */
    .cognitive-coverage {
        background: var(--bg-elevated);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-md);
        padding: var(--space-3);
        margin: var(--space-2) 0;
    }
    .coverage-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--space-2);
    }
    .coverage-label {
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        color: var(--text-muted);
        letter-spacing: 0.05em;
    }
    .coverage-percent {
        font-size: 12px;
        font-weight: 600;
        color: var(--accent);
    }
    .coverage-bars {
        display: flex;
        gap: 6px;
    }
    .coverage-bar {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 3px;
        padding: 6px 4px;
        background: var(--bg-base);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-sm);
        opacity: 0.5;
        transition: all 0.2s ease;
    }
    .coverage-bar--active {
        opacity: 1;
        background: color-mix(in srgb, var(--accent) 10%, var(--bg-base));
        border-color: color-mix(in srgb, var(--accent) 40%, var(--border-light));
    }
    .bar-icon {
        font-size: 14px;
    }
    .bar-label {
        font-size: 9px;
        color: var(--text-muted);
        text-transform: uppercase;
        font-weight: 500;
    }
    .bar-count {
        font-size: 12px;
        font-weight: 600;
        color: var(--text-secondary);
    }
    .coverage-bar--active .bar-count {
        color: var(--accent);
    }

    /* Question Response Card - Interactive Thinking Dialogue */
    .question-response-card {
        background: linear-gradient(135deg,
            color-mix(in srgb, var(--class-color, #888) 8%, var(--bg-base)),
            color-mix(in srgb, var(--class-color, #888) 4%, var(--bg-elevated))
        );
        border: 2px solid color-mix(in srgb, var(--class-color, #888) 40%, var(--border-light));
        border-radius: var(--radius-lg);
        padding: var(--space-4);
        margin: var(--space-3) 0;
        box-shadow: var(--shadow-md),
            0 0 20px color-mix(in srgb, var(--class-color, #888) 15%, transparent);
        animation: qrc-appear 0.3s ease-out;
    }
    @keyframes qrc-appear {
        from {
            opacity: 0;
            transform: translateY(-10px) scale(0.98);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }

    .qrc-header {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        margin-bottom: var(--space-3);
    }
    .qrc-icon {
        font-size: 20px;
        line-height: 1;
    }
    .qrc-label {
        font-family: var(--font-display);
        font-size: 14px;
        font-weight: 600;
        color: var(--class-color, var(--text-primary));
        flex: 1;
    }
    .qrc-badge {
        font-size: 10px;
        padding: 3px 8px;
        background: color-mix(in srgb, var(--class-color, #888) 20%, var(--bg-elevated));
        color: var(--class-color, var(--text-secondary));
        border-radius: var(--radius-full);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .qrc-question {
        font-size: 15px;
        line-height: 1.6;
        color: var(--text-primary);
        font-weight: 500;
        padding: var(--space-3);
        background: var(--bg-elevated);
        border-radius: var(--radius-md);
        border-left: 3px solid var(--class-color, var(--accent));
        margin-bottom: var(--space-3);
    }

    .qrc-hint {
        background: color-mix(in srgb, var(--class-color, #888) 6%, var(--bg-base));
        border-radius: var(--radius-sm);
        padding: var(--space-3);
        margin-bottom: var(--space-3);
        border: 1px dashed color-mix(in srgb, var(--class-color, #888) 25%, var(--border-light));
    }
    .qrc-hint-text {
        font-size: 12px;
        color: var(--text-secondary);
        margin: 0 0 var(--space-2);
        line-height: 1.5;
    }
    .qrc-hint-prompt {
        font-size: 12px;
        color: var(--text-muted);
        margin: 0;
        font-style: italic;
    }
    .qrc-hint-prompt strong {
        color: var(--class-color, var(--accent));
        font-style: normal;
    }

    .qrc-input {
        width: 100%;
        resize: vertical;
        min-height: 80px;
        border: 2px solid var(--border-light);
        border-radius: var(--radius-md);
        padding: var(--space-3);
        font-size: 14px;
        font-family: var(--font-body);
        background: var(--bg-elevated);
        color: var(--text-primary);
        transition: all 0.2s ease;
        margin-bottom: var(--space-3);
    }
    .qrc-input:focus {
        outline: none;
        border-color: var(--class-color, var(--accent));
        box-shadow: 0 0 0 4px color-mix(in srgb, var(--class-color, var(--accent)) 15%, transparent);
    }
    .qrc-input::placeholder {
        color: var(--text-subtle);
    }
    .qrc-input:disabled {
        opacity: 0.7;
        cursor: not-allowed;
    }

    .qrc-actions {
        display: flex;
        flex-direction: column;
        gap: var(--space-2);
    }
    .qrc-starter {
        font-size: 12px;
        padding: var(--space-2) var(--space-3);
        background: var(--bg-base);
        color: var(--class-color, var(--text-secondary));
        border: 1px solid color-mix(in srgb, var(--class-color, #888) 30%, var(--border-light));
        border-radius: var(--radius-sm);
        cursor: pointer;
        text-align: left;
        transition: all 0.15s ease;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .qrc-starter:hover:not(:disabled) {
        background: color-mix(in srgb, var(--class-color, #888) 10%, var(--bg-base));
        border-color: var(--class-color, var(--accent));
    }
    .qrc-starter:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .qrc-buttons {
        display: flex;
        gap: var(--space-2);
        justify-content: flex-end;
    }
    .qrc-skip {
        font-size: 13px;
        padding: var(--space-2) var(--space-4);
        background: var(--bg-elevated);
        color: var(--text-muted);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-sm);
        cursor: pointer;
        transition: all 0.15s ease;
    }
    .qrc-skip:hover:not(:disabled) {
        background: var(--bg-base);
        color: var(--text-secondary);
    }
    .qrc-skip:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .qrc-respond {
        font-size: 13px;
        padding: var(--space-2) var(--space-5);
        background: var(--class-color, var(--accent));
        color: white;
        border: none;
        border-radius: var(--radius-sm);
        cursor: pointer;
        font-weight: 600;
        transition: all 0.15s ease;
        min-width: 100px;
    }
    .qrc-respond:hover:not(:disabled) {
        filter: brightness(1.1);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px color-mix(in srgb, var(--class-color, var(--accent)) 30%, transparent);
    }
    .qrc-respond:disabled {
        opacity: 0.5;
        cursor: not-allowed;
        transform: none;
    }

    .qrc-history {
        margin-top: var(--space-3);
        padding-top: var(--space-2);
        border-top: 1px solid var(--border-subtle);
    }
    .qrc-history-label {
        font-size: 11px;
        color: var(--text-muted);
        font-style: italic;
    }
</style>
