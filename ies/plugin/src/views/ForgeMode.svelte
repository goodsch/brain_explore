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
     *
     * Phase 4 Updates: Session documents aligned with ShapingBlockMeta
     * - block_type: 'shaping' in frontmatter and attributes
     * - session_id, thinking_mode, phase tracking
     * - Saves to /Sessions/{mode}/ folders using merged folder structure
     */
    import { onMount, createEventDispatcher } from 'svelte';
    import { showMessage, getFrontend, fetchSyncPost } from 'siyuan';
    import { createSessionDocument, resolveStructureNotebook } from '../utils/siyuan-structure';
    import ConceptExtractor from '../components/ConceptExtractor.svelte';

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
    let status: 'idle' | 'starting' | 'active' | 'error' | 'extracting' = 'idle';
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

    // Concept extraction state (P3: Virtuous Cycle - formalize insights as concepts)
    interface SessionEndData {
        docId: string | null;
        entitiesCreated: string[];
        entitiesUpdated: string[];
        keyInsights: string[];
        openQuestions: string[];
    }
    let sessionEndData: SessionEndData | null = null;
    let selectedForExtraction: Set<string> = new Set();
    let extractionDefinitions: Record<string, string> = {};
    let isCreatingConcept = false;

    // Advanced Concept Extractor modal state (with backend Neo4j integration)
    let showConceptExtractor = false;
    let extractorEntityName: string | null = null;

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

    /**
     * Determine the phase of the session based on question classes used and session progress.
     * Phase 4: Add phase tracking for ShapingBlockMeta
     */
    function determineSessionPhase(): 'exploration' | 'challenge' | 'synthesis' | 'meta' {
        if (questionClassesUsed.length === 0) {
            return 'exploration'; // Default phase at start
        }

        // Count question class categories
        const hasStructure = questionClassesUsed.some(qc => ['schema_probe', 'boundary', 'dimensional'].includes(qc));
        const hasMechanism = questionClassesUsed.some(qc => ['causal', 'counterfactual'].includes(qc));
        const hasGrounding = questionClassesUsed.some(qc => ['anchor', 'perspective_shift'].includes(qc));
        const hasMeta = questionClassesUsed.some(qc => ['meta_cognitive', 'reflective_synthesis'].includes(qc));

        // Determine phase based on predominant question types
        if (hasMeta) {
            return 'meta'; // Meta-cognitive or synthesis questions indicate reflection phase
        } else if (hasStructure && hasMechanism && hasGrounding) {
            return 'synthesis'; // Multiple dimensions explored, moving toward integration
        } else if (hasMechanism || hasGrounding) {
            return 'challenge'; // Digging deeper with causal or grounding questions
        } else {
            return 'exploration'; // Initial exploration with structure questions
        }
    }

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

            // Determine session phase based on question classes used (Phase 4)
            const sessionPhase = determineSessionPhase();

            // Create session document in SiYuan with ShapingBlockMeta fields (Phase 4)
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
                thinking_mode: selectedMode, // Phase 4: Add thinking_mode for ShapingBlockMeta
                phase: sessionPhase, // Phase 4: Add phase tracking for ShapingBlockMeta
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

            // P3: Check if there are concepts/insights to potentially extract
            const hasExtractableContent =
                (data.entities_created?.length > 0) ||
                (data.key_insights?.length > 0);

            if (hasExtractableContent) {
                // Store session end data for extraction UI
                sessionEndData = {
                    docId: data.doc_id,
                    entitiesCreated: data.entities_created || [],
                    entitiesUpdated: data.entities_updated || [],
                    keyInsights: data.key_insights || [],
                    openQuestions: data.open_questions || []
                };
                // Pre-select all new entities for extraction
                selectedForExtraction = new Set(data.entities_created || []);
                extractionDefinitions = {};
                status = 'extracting';
                // Keep sessionId for reference but clear conversation state
                sessionId = null;
                messages = [];
            } else {
                // No extractable content - reset fully
                resetToIdle();
            }
        } catch (err) {
            console.error('[IES] End error:', err);
            status = 'error';
            errorMsg = err.message;
            showMessage(`Error: ${err.message}`, 5000, 'error');
        }
    }

    // P3: Reset to idle state (extracted to avoid duplication)
    function resetToIdle() {
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
        sessionEndData = null;
        selectedForExtraction = new Set();
        extractionDefinitions = {};
    }

    // P3: Toggle entity selection for extraction
    function toggleExtractionSelection(entityName: string) {
        if (selectedForExtraction.has(entityName)) {
            selectedForExtraction.delete(entityName);
        } else {
            selectedForExtraction.add(entityName);
        }
        selectedForExtraction = selectedForExtraction; // Trigger reactivity
    }

    // P3: Create concept documents for selected entities
    async function createSelectedConcepts() {
        if (selectedForExtraction.size === 0) {
            showMessage('Select at least one concept to extract', 3000, 'info');
            return;
        }

        isCreatingConcept = true;
        let created = 0;

        try {
            for (const entityName of selectedForExtraction) {
                const definition = extractionDefinitions[entityName] || '';
                await createConceptDocument(entityName, definition, sessionEndData);
                created++;
            }

            showMessage(`Created ${created} concept document${created > 1 ? 's' : ''} in /Concepts/`, 4000);
            resetToIdle();
        } catch (err) {
            console.error('[IES] Concept creation error:', err);
            showMessage(`Error creating concepts: ${err.message}`, 5000, 'error');
        } finally {
            isCreatingConcept = false;
        }
    }

    // P3: Skip extraction and reset to idle
    function skipExtraction() {
        showMessage('Session complete. Skipped concept extraction.', 3000, 'info');
        resetToIdle();
    }

    // P3: Open advanced ConceptExtractor modal for detailed extraction with Neo4j integration
    function openAdvancedExtractor(entityName: string) {
        extractorEntityName = entityName;
        showConceptExtractor = true;
    }

    // P3: Handle completion of ConceptExtractor (concept saved to Neo4j + SiYuan)
    function handleExtractionComplete(event: CustomEvent<{
        conceptId: string;
        name: string;
        docId: string | null;
    }>) {
        const { conceptId, name, docId } = event.detail;
        showConceptExtractor = false;
        extractorEntityName = null;

        // Remove from pending selection if it was there
        if (selectedForExtraction.has(name)) {
            selectedForExtraction.delete(name);
            selectedForExtraction = selectedForExtraction; // Trigger reactivity
        }

        showMessage(`✅ Concept "${name}" saved to knowledge graph${docId ? ' and SiYuan' : ''}`, 4000);

        // If no more entities to extract, can reset
        if (selectedForExtraction.size === 0 && sessionEndData) {
            // Offer to finish or continue
            showMessage('All selected concepts extracted. Click "Skip & Finish" to complete.', 5000, 'info');
        }
    }

    // P3: Handle ConceptExtractor close (cancel)
    function handleExtractionClose() {
        showConceptExtractor = false;
        extractorEntityName = null;
    }

    // P3: Create a concept document in SiYuan /Concepts/ folder
    async function createConceptDocument(name: string, definition: string, sessionData: SessionEndData | null) {
        const notebook = await resolveStructureNotebook();
        if (!notebook) {
            throw new Error('No notebook available for concept creation');
        }

        // Ensure /Concepts/ folder exists
        const conceptsPath = '/Concepts';
        await ensureFolderExists(notebook, conceptsPath);

        // Generate safe filename
        const safeTitle = name.replace(/[\/\\:*?"<>|]/g, '-').substring(0, 50);
        const timestamp = new Date().toISOString().split('T')[0];
        const filePath = `${conceptsPath}/${timestamp}-${safeTitle}`;

        // Build frontmatter
        const frontmatter = {
            be_type: 'concept',
            be_id: `concept_${Date.now()}`,
            name: name,
            status: 'draft',
            created: new Date().toISOString(),
            source_session: sessionData?.docId || null,
            source_mode: selectedMode,
            source_topic: sessionTopic
        };

        // Build document content
        const content = `---
${Object.entries(frontmatter).map(([k, v]) => `${k}: ${JSON.stringify(v)}`).join('\n')}
---

# ${name}

## Definition
${definition || '*Add a definition for this concept...*'}

## Context
This concept emerged from a ${THINKING_MODES[selectedMode]?.name || selectedMode} session on "${sessionTopic}".

## Related Concepts
${sessionData?.entitiesCreated?.filter(e => e !== name).map(e => `- [[${e}]]`).join('\n') || '*No related concepts identified*'}

## Open Questions
${sessionData?.openQuestions?.map(q => `- ${q}`).join('\n') || '*No open questions recorded*'}

## Notes
*Add additional notes about this concept...*
`;

        // Create the document via SiYuan API
        const response = await fetchSyncPost('/api/filetree/createDocWithMd', {
            notebook: notebook,
            path: filePath,
            markdown: content
        });

        if (response.code !== 0) {
            throw new Error(response.msg || 'Failed to create concept document');
        }

        return response.data;
    }

    // Helper: Ensure folder exists in notebook
    async function ensureFolderExists(notebook: string, path: string) {
        try {
            await fetchSyncPost('/api/filetree/createDocWithMd', {
                notebook: notebook,
                path: path,
                markdown: `# ${path.split('/').pop()}\n\n*Folder created by IES plugin*`
            });
        } catch (e) {
            // Folder may already exist, ignore error
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

<!-- Rest of the component remains unchanged from line 862 onward -->
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

            {:else if status === 'extracting' && sessionEndData}
                <!-- P3: Concept Extraction Flow - Formalize insights from session -->
                <div class="extraction-panel">
                    <div class="extraction-header">
                        <h3>📝 Session Complete - Extract Concepts?</h3>
                        <p class="extraction-subtitle">
                            {sessionEndData.entitiesCreated.length + sessionEndData.entitiesUpdated.length} entities discovered.
                            Select any to formalize as concept documents.
                        </p>
                    </div>

                    <!-- Key Insights Summary -->
                    {#if sessionEndData.keyInsights.length > 0}
                        <div class="extraction-section">
                            <h4>💡 Key Insights</h4>
                            <ul class="insights-list">
                                {#each sessionEndData.keyInsights as insight}
                                    <li>{insight}</li>
                                {/each}
                            </ul>
                        </div>
                    {/if}

                    <!-- Entity Selection -->
                    <div class="extraction-section">
                        <h4>🔗 Discovered Entities</h4>
                        <p class="extraction-hint">Check for quick extract, or click "Advanced" for full wizard with relationships</p>
                        <div class="entity-selection-grid">
                            {#each [...sessionEndData.entitiesCreated, ...sessionEndData.entitiesUpdated] as entity}
                                <div class="entity-row">
                                    <label class="entity-checkbox" class:selected={selectedForExtraction.has(entity)}>
                                        <input
                                            type="checkbox"
                                            checked={selectedForExtraction.has(entity)}
                                            on:change={() => toggleExtractionSelection(entity)}
                                        />
                                        <span class="entity-name">{entity}</span>
                                        {#if sessionEndData.entitiesCreated.includes(entity)}
                                            <span class="entity-badge new">new</span>
                                        {:else}
                                            <span class="entity-badge updated">updated</span>
                                        {/if}
                                    </label>
                                    <button
                                        class="entity-advanced-btn"
                                        on:click={() => openAdvancedExtractor(entity)}
                                        title="Open advanced concept wizard with relationships"
                                    >
                                        Advanced →
                                    </button>
                                </div>
                            {/each}
                        </div>
                    </div>

                    <!-- Definition Input for Selected Entities -->
                    {#if selectedForExtraction.size > 0}
                        <div class="extraction-section">
                            <h4>📖 Define Selected Concepts</h4>
                            <p class="definition-hint">Add a brief definition for each concept to create in /Concepts/</p>
                            {#each [...selectedForExtraction] as entity}
                                <div class="definition-input-group">
                                    <label>{entity}</label>
                                    <textarea
                                        bind:value={extractionDefinitions[entity]}
                                        placeholder="What does {entity} mean in your understanding?"
                                        rows="2"
                                    ></textarea>
                                </div>
                            {/each}
                        </div>
                    {/if}

                    <!-- Open Questions -->
                    {#if sessionEndData.openQuestions.length > 0}
                        <div class="extraction-section">
                            <h4>❓ Open Questions</h4>
                            <ul class="questions-list">
                                {#each sessionEndData.openQuestions as question}
                                    <li>{question}</li>
                                {/each}
                            </ul>
                        </div>
                    {/if}

                    <!-- Actions -->
                    <div class="extraction-actions">
                        <button
                            class="b3-button"
                            on:click={skipExtraction}
                            disabled={isCreatingConcept}
                        >
                            Skip & Finish
                        </button>
                        <button
                            class="b3-button b3-button--primary"
                            on:click={createSelectedConcepts}
                            disabled={selectedForExtraction.size === 0 || isCreatingConcept}
                        >
                            {#if isCreatingConcept}
                                Creating...
                            {:else}
                                Create {selectedForExtraction.size} Concept{selectedForExtraction.size !== 1 ? 's' : ''}
                            {/if}
                        </button>
                    </div>
                </div>

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

<!-- P3: Advanced Concept Extractor Modal (with Neo4j integration) -->
{#if showConceptExtractor && extractorEntityName && sessionEndData}
    <ConceptExtractor
        {backendUrl}
        initialEntityName={extractorEntityName}
        sessionData={{
            sessionId: sessionId || `session_${Date.now()}`,
            mode: selectedMode,
            topic: sessionTopic,
            transcript: messages.map(m => `${m.role === 'user' ? 'You' : 'AI'}: ${m.content}`).join('\n\n'),
            entities: [...sessionEndData.entitiesCreated, ...sessionEndData.entitiesUpdated],
            insights: sessionEndData.keyInsights
        }}
        on:complete={handleExtractionComplete}
        on:close={handleExtractionClose}
    />
{/if}

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

    /* ... rest of the styles unchanged ... */
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

    /* ============================================
       INTERACTIVE QUESTION RESPONSE CARD
       ============================================ */
    .question-response-card {
        background: var(--bg-elevated);
        border: 2px solid var(--class-color, var(--accent));
        border-radius: var(--radius-md);
        padding: var(--space-4);
        margin: var(--space-3) 0;
        box-shadow: var(--shadow-md);
    }

    .qrc-header {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        margin-bottom: var(--space-3);
    }

    .qrc-icon {
        font-size: 1.25rem;
    }

    .qrc-label {
        font-family: var(--font-display);
        font-weight: 600;
        font-size: 0.9rem;
        color: var(--class-color, var(--accent));
    }

    .qrc-badge {
        margin-left: auto;
        font-size: 0.7rem;
        padding: 2px 8px;
        background: var(--accent-lighter);
        color: var(--accent);
        border-radius: var(--radius-full);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .qrc-question {
        font-size: 1rem;
        line-height: 1.6;
        color: var(--text-primary);
        margin-bottom: var(--space-3);
        padding: var(--space-3);
        background: var(--bg-base);
        border-radius: var(--radius-sm);
        border-left: 3px solid var(--class-color, var(--accent));
    }

    .qrc-hint {
        background: var(--secondary-lighter);
        border-radius: var(--radius-sm);
        padding: var(--space-3);
        margin-bottom: var(--space-3);
    }

    .qrc-hint-text {
        font-size: 0.85rem;
        color: var(--text-secondary);
        margin: 0 0 var(--space-2) 0;
        line-height: 1.5;
    }

    .qrc-hint-prompt {
        font-size: 0.85rem;
        color: var(--secondary);
        margin: 0;
    }

    .qrc-input {
        width: 100%;
        padding: var(--space-3);
        border: 1px solid var(--border-medium);
        border-radius: var(--radius-sm);
        background: var(--bg-base);
        color: var(--text-primary);
        font-family: var(--font-body);
        font-size: 0.95rem;
        line-height: 1.5;
        resize: vertical;
        min-height: 80px;
        transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }

    .qrc-input:focus {
        outline: none;
        border-color: var(--class-color, var(--accent));
        box-shadow: 0 0 0 3px color-mix(in srgb, var(--class-color, var(--accent)) 20%, transparent);
    }

    .qrc-input::placeholder {
        color: var(--text-subtle);
    }

    .qrc-input:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .qrc-actions {
        display: flex;
        flex-direction: column;
        gap: var(--space-2);
        margin-top: var(--space-3);
    }

    .qrc-starter {
        background: var(--bg-base);
        border: 1px dashed var(--border-medium);
        border-radius: var(--radius-sm);
        padding: var(--space-2) var(--space-3);
        font-size: 0.8rem;
        color: var(--text-muted);
        cursor: pointer;
        text-align: left;
        transition: all 0.15s ease;
    }

    .qrc-starter:hover:not(:disabled) {
        background: var(--secondary-lighter);
        border-color: var(--secondary);
        color: var(--secondary);
    }

    .qrc-starter:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .qrc-buttons {
        display: flex;
        justify-content: flex-end;
        gap: var(--space-2);
    }

    .qrc-skip {
        background: transparent;
        border: 1px solid var(--border-light);
        border-radius: var(--radius-sm);
        padding: var(--space-2) var(--space-4);
        font-size: 0.85rem;
        color: var(--text-muted);
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
        background: var(--class-color, var(--accent));
        border: none;
        border-radius: var(--radius-sm);
        padding: var(--space-2) var(--space-5);
        font-size: 0.85rem;
        font-weight: 600;
        color: white;
        cursor: pointer;
        transition: all 0.15s ease;
    }

    .qrc-respond:hover:not(:disabled) {
        filter: brightness(1.1);
        transform: translateY(-1px);
    }

    .qrc-respond:active:not(:disabled) {
        transform: translateY(0);
    }

    .qrc-respond:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .qrc-history {
        margin-top: var(--space-3);
        padding-top: var(--space-2);
        border-top: 1px solid var(--border-subtle);
    }

    .qrc-history-label {
        font-size: 0.75rem;
        color: var(--text-muted);
    }

    /* ============================================
       CONVERSATION MESSAGES
       ============================================ */
    .forge-messages {
        flex: 1;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: var(--space-2);
        padding: var(--space-2);
    }

    .message {
        padding: var(--space-3);
        border-radius: var(--radius-md);
        max-width: 85%;
    }

    .message.user {
        align-self: flex-end;
        background: var(--accent-lighter);
        color: var(--text-primary);
    }

    .message.assistant {
        align-self: flex-start;
        background: var(--bg-elevated);
        border: 1px solid var(--border-subtle);
    }

    /* ============================================
       INPUT AREA
       ============================================ */
    .forge-input {
        display: flex;
        gap: var(--space-2);
        padding: var(--space-2);
        background: var(--bg-base);
        border-radius: var(--radius-md);
        border: 1px solid var(--border-light);
    }

    .forge-input textarea {
        flex: 1;
        border: none;
        background: transparent;
        color: var(--text-primary);
        font-family: var(--font-body);
        font-size: 0.95rem;
        resize: none;
        padding: var(--space-2);
    }

    .forge-input textarea:focus {
        outline: none;
    }

    .forge-input textarea::placeholder {
        color: var(--text-subtle);
    }

    .forge-controls {
        display: flex;
        gap: var(--space-2);
        align-items: flex-end;
    }

    .send-btn {
        background: var(--accent);
        border: none;
        border-radius: var(--radius-sm);
        padding: var(--space-2) var(--space-4);
        color: white;
        font-weight: 600;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: var(--space-1);
        transition: all 0.15s ease;
    }

    .send-btn:hover:not(:disabled) {
        background: var(--accent-dark);
    }

    .send-btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .end-btn {
        background: var(--secondary);
        border: none;
        border-radius: var(--radius-sm);
        padding: var(--space-2) var(--space-3);
        color: white;
        font-size: 0.85rem;
        cursor: pointer;
        transition: all 0.15s ease;
    }

    .end-btn:hover {
        filter: brightness(1.1);
    }

    /* ============================================
       TEMPLATE PROGRESS
       ============================================ */
    .template-progress {
        padding: var(--space-3);
        background: var(--bg-elevated);
        border-radius: var(--radius-md);
        border: 1px solid var(--border-subtle);
    }

    .progress-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--space-2);
    }

    .progress-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--text-secondary);
    }

    .progress-count {
        font-size: 0.75rem;
        color: var(--text-muted);
    }

    .progress-bar {
        height: 4px;
        background: var(--border-light);
        border-radius: 2px;
        overflow: hidden;
    }

    .progress-fill {
        height: 100%;
        background: var(--accent);
        border-radius: 2px;
        transition: width 0.3s ease;
    }

    .current-section {
        margin-top: var(--space-2);
        font-size: 0.8rem;
        color: var(--accent);
    }

    /* ============================================
       SESSION SUMMARY
       ============================================ */
    .session-summary {
        padding: var(--space-4);
        background: var(--bg-elevated);
        border-radius: var(--radius-md);
        border: 1px solid var(--border-subtle);
    }

    .summary-title {
        font-family: var(--font-display);
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: var(--space-3);
        color: var(--text-primary);
    }

    .summary-stats {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: var(--space-3);
    }

    .stat-item {
        text-align: center;
        padding: var(--space-2);
        background: var(--bg-base);
        border-radius: var(--radius-sm);
    }

    .stat-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--accent);
    }

    .stat-label {
        font-size: 0.75rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* ============================================
       QUESTION HINT PANEL - COGNITIVE GUIDANCE
       ============================================ */
    .question-hint-panel {
        position: sticky;
        bottom: var(--space-3);
        background: var(--bg-elevated);
        border: 2px solid var(--class-color, var(--accent));
        border-radius: var(--radius-md);
        margin-top: var(--space-3);
        box-shadow: var(--shadow-md);
        overflow: hidden;
    }

    .question-hint-panel--expanded {
        box-shadow: var(--shadow-lg);
    }

    .question-hint-header {
        width: 100%;
        display: flex;
        align-items: center;
        gap: var(--space-2);
        padding: var(--space-3);
        background: color-mix(in srgb, var(--class-color, var(--accent)) 10%, var(--bg-elevated));
        border: none;
        cursor: pointer;
        text-align: left;
        transition: background 0.15s ease;
    }

    .question-hint-header:hover {
        background: color-mix(in srgb, var(--class-color, var(--accent)) 15%, var(--bg-elevated));
    }

    .question-hint-icon {
        font-size: 1.1rem;
    }

    .question-hint-type {
        font-family: var(--font-display);
        font-weight: 600;
        font-size: 0.85rem;
        color: var(--class-color, var(--accent));
        flex: 1;
    }

    .question-hint-toggle {
        font-size: 0.7rem;
        color: var(--text-muted);
        transition: transform 0.15s ease;
    }

    .question-hint-panel--expanded .question-hint-toggle {
        transform: rotate(0deg);
    }

    .question-hint-content {
        padding: var(--space-3);
        background: var(--bg-base);
        border-top: 1px solid var(--border-subtle);
    }

    .question-hint-text {
        font-size: 0.9rem;
        color: var(--text-secondary);
        margin: 0 0 var(--space-2) 0;
        line-height: 1.5;
    }

    .question-hint-prompt {
        font-size: 0.85rem;
        color: var(--class-color, var(--accent));
        margin: 0 0 var(--space-2) 0;
    }

    .question-hint-starter {
        background: var(--bg-elevated);
        border: 1px dashed var(--class-color, var(--border-medium));
        border-radius: var(--radius-sm);
        padding: var(--space-2) var(--space-3);
        font-size: 0.8rem;
        color: var(--text-muted);
        cursor: pointer;
        width: 100%;
        text-align: left;
        transition: all 0.15s ease;
        margin-top: var(--space-2);
    }

    .question-hint-starter:hover {
        background: color-mix(in srgb, var(--class-color, var(--accent)) 10%, var(--bg-elevated));
        border-color: var(--class-color, var(--accent));
        color: var(--class-color, var(--accent));
    }

    .question-hint-dismiss {
        position: absolute;
        top: var(--space-2);
        right: var(--space-2);
        background: none;
        border: none;
        font-size: 1.25rem;
        color: var(--text-muted);
        cursor: pointer;
        padding: var(--space-1);
        line-height: 1;
        opacity: 0.6;
        transition: opacity 0.15s ease;
    }

    .question-hint-dismiss:hover {
        opacity: 1;
        color: var(--text-secondary);
    }

    /* ============================================
       MODE TRANSITION SUGGESTION
       ============================================ */
    .mode-transition-suggestion {
        background: linear-gradient(135deg, var(--tertiary-light) 0%, var(--secondary-lighter) 100%);
        border: 1px solid var(--tertiary);
        border-radius: var(--radius-md);
        padding: var(--space-3);
        margin-top: var(--space-3);
        animation: suggestPulse 2s ease-in-out infinite;
    }

    @keyframes suggestPulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.9; }
    }

    .suggestion-content {
        display: flex;
        align-items: flex-start;
        gap: var(--space-3);
    }

    .suggestion-icon {
        font-size: 1.5rem;
        line-height: 1;
    }

    .suggestion-text {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: var(--space-1);
    }

    .suggestion-label {
        font-family: var(--font-display);
        font-weight: 600;
        font-size: 0.9rem;
        color: var(--tertiary);
    }

    .suggestion-reason {
        font-size: 0.8rem;
        color: var(--text-secondary);
        line-height: 1.4;
    }

    .suggestion-actions {
        display: flex;
        gap: var(--space-2);
        margin-top: var(--space-3);
    }

    .suggestion-accept {
        background: var(--tertiary);
        border: none;
        border-radius: var(--radius-sm);
        padding: var(--space-2) var(--space-4);
        font-size: 0.85rem;
        font-weight: 600;
        color: white;
        cursor: pointer;
        transition: all 0.15s ease;
    }

    .suggestion-accept:hover {
        filter: brightness(1.1);
        transform: translateY(-1px);
    }

    .suggestion-dismiss {
        background: transparent;
        border: 1px solid var(--border-light);
        border-radius: var(--radius-sm);
        padding: var(--space-2) var(--space-3);
        font-size: 0.85rem;
        color: var(--text-muted);
        cursor: pointer;
        transition: all 0.15s ease;
    }

    .suggestion-dismiss:hover {
        background: var(--bg-elevated);
        color: var(--text-secondary);
    }

    /* ============================================
       EXPLORATION PATH DISPLAY
       ============================================ */
    .exploration-path {
        display: flex;
        flex-wrap: wrap;
        gap: var(--space-1);
        padding: var(--space-2);
        background: var(--bg-base);
        border-radius: var(--radius-sm);
        margin-bottom: var(--space-2);
    }

    .path-step {
        font-size: 0.75rem;
        padding: 2px 6px;
        background: var(--accent-lighter);
        color: var(--accent);
        border-radius: var(--radius-sm);
    }

    .path-arrow {
        font-size: 0.7rem;
        color: var(--text-subtle);
    }

    /* ============================================
       COVERAGE STATS
       ============================================ */
    .coverage-stats {
        display: flex;
        flex-wrap: wrap;
        gap: var(--space-2);
        padding: var(--space-3);
        background: var(--bg-base);
        border-radius: var(--radius-sm);
        margin-top: var(--space-2);
    }

    .coverage-item {
        display: flex;
        align-items: center;
        gap: var(--space-1);
        font-size: 0.75rem;
    }

    .coverage-badge {
        width: 8px;
        height: 8px;
        border-radius: 50%;
    }

    .coverage-badge--covered {
        background: var(--secondary);
    }

    .coverage-badge--uncovered {
        background: var(--border-medium);
    }

    .coverage-label {
        color: var(--text-muted);
    }

    .coverage-count {
        font-weight: 600;
        color: var(--text-secondary);
    }

    /* ============================================
       SETUP SECTION (Mode Selection)
       ============================================ */
    .forge-setup {
        display: flex;
        flex-direction: column;
        gap: var(--space-4);
        padding: var(--space-4);
        background: var(--bg-base);
        border-radius: var(--radius-md);
    }

    .setup-section {
        display: flex;
        flex-direction: column;
        gap: var(--space-2);
    }

    .setup-label {
        font-family: var(--font-display);
        font-weight: 600;
        font-size: 0.9rem;
        color: var(--text-secondary);
    }

    .mode-selector {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: var(--space-2);
    }

    .mode-option {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: var(--space-2);
        padding: var(--space-3);
        background: var(--bg-elevated);
        border: 2px solid var(--border-subtle);
        border-radius: var(--radius-md);
        cursor: pointer;
        transition: all 0.15s ease;
    }

    .mode-option:hover {
        border-color: var(--accent);
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }

    .mode-option.selected {
        border-color: var(--accent);
        background: var(--accent-lighter);
    }

    .mode-option-icon {
        font-size: 1.5rem;
    }

    .mode-option-name {
        font-weight: 600;
        font-size: 0.85rem;
        color: var(--text-primary);
    }

    .mode-option-desc {
        font-size: 0.75rem;
        color: var(--text-muted);
        text-align: center;
    }

    .topic-input {
        width: 100%;
        padding: var(--space-3);
        border: 1px solid var(--border-medium);
        border-radius: var(--radius-sm);
        background: var(--bg-elevated);
        color: var(--text-primary);
        font-family: var(--font-body);
        font-size: 0.95rem;
        line-height: 1.5;
        resize: vertical;
        min-height: 80px;
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
        background: var(--accent);
        border: none;
        border-radius: var(--radius-sm);
        padding: var(--space-3) var(--space-5);
        font-family: var(--font-body);
        font-size: 1rem;
        font-weight: 600;
        color: white;
        cursor: pointer;
        transition: all 0.15s ease;
        align-self: flex-start;
    }

    .start-btn:hover:not(:disabled) {
        background: var(--accent-dark);
        transform: translateY(-1px);
    }

    .start-btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    /* ============================================
       FORGE MAIN CONVERSATION AREA
       ============================================ */
    .forge-main {
        display: flex;
        flex-direction: column;
        flex: 1;
        gap: var(--space-3);
        min-height: 0;
    }

    .forge-conversation {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: var(--space-2);
        overflow-y: auto;
        padding: var(--space-2);
        background: var(--bg-base);
        border-radius: var(--radius-md);
    }

    .forge-msg {
        padding: var(--space-3);
        border-radius: var(--radius-md);
        max-width: 90%;
        line-height: 1.6;
    }

    .forge-msg.user {
        align-self: flex-end;
        background: var(--accent-lighter);
        color: var(--text-primary);
    }

    .forge-msg.assistant {
        align-self: flex-start;
        background: var(--bg-elevated);
        border: 1px solid var(--border-subtle);
    }

    .forge-loading {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        padding: var(--space-3);
        background: var(--bg-elevated);
        border-radius: var(--radius-md);
        align-self: flex-start;
    }

    .forge-loading::after {
        content: '';
        width: 20px;
        height: 20px;
        border: 2px solid var(--border-medium);
        border-top-color: var(--accent);
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    .forge-error {
        padding: var(--space-3);
        background: color-mix(in srgb, var(--error, #dc2626) 10%, var(--bg-elevated));
        border: 1px solid var(--error, #dc2626);
        border-radius: var(--radius-sm);
        color: var(--error, #dc2626);
        font-size: 0.9rem;
    }

    .forge-actions {
        display: flex;
        justify-content: flex-end;
        gap: var(--space-2);
        padding-top: var(--space-2);
    }

    /* ============================================
       TEMPLATE PROGRESS SECTIONS
       ============================================ */
    .forge-progress {
        background: var(--bg-elevated);
        border-radius: var(--radius-md);
        border: 1px solid var(--border-subtle);
        overflow: hidden;
    }

    .progress-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: var(--space-3);
        background: var(--bg-base);
        border-bottom: 1px solid var(--border-subtle);
    }

    .progress-title {
        font-family: var(--font-display);
        font-weight: 600;
        font-size: 0.95rem;
        color: var(--text-primary);
    }

    .progress-count {
        font-size: 0.8rem;
        color: var(--text-muted);
    }

    .progress-sections {
        display: flex;
        flex-direction: column;
    }

    .progress-section {
        padding: var(--space-3);
        border-bottom: 1px solid var(--border-subtle);
        cursor: pointer;
        transition: background 0.15s ease;
    }

    .progress-section:last-child {
        border-bottom: none;
    }

    .progress-section:hover {
        background: var(--bg-base);
    }

    .progress-section.current {
        background: var(--accent-lighter);
        border-left: 3px solid var(--accent);
    }

    .progress-section.completed {
        opacity: 0.7;
    }

    .progress-section-header {
        display: flex;
        align-items: center;
        gap: var(--space-2);
    }

    .progress-section-icon {
        font-size: 0.9rem;
    }

    .progress-section-label {
        font-weight: 500;
        font-size: 0.85rem;
        color: var(--text-primary);
    }

    .progress-section-response {
        margin-top: var(--space-2);
        font-size: 0.8rem;
        color: var(--text-muted);
        line-height: 1.4;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }

    .progress-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: var(--space-3);
        background: var(--bg-base);
        border-top: 1px solid var(--border-subtle);
    }

    .progress-footer-label {
        font-size: 0.8rem;
        color: var(--text-muted);
    }

    .progress-actions {
        display: flex;
        gap: var(--space-2);
    }

    .progress-action {
        background: var(--secondary);
        border: none;
        border-radius: var(--radius-sm);
        padding: var(--space-2) var(--space-3);
        font-size: 0.8rem;
        font-weight: 600;
        color: white;
        cursor: pointer;
        transition: all 0.15s ease;
    }

    .progress-action:hover {
        filter: brightness(1.1);
    }

    .progress-action.primary {
        background: var(--accent);
    }

    /* ============================================
       QUESTION CLASS BADGES & COVERAGE
       ============================================ */
    .question-class-badges {
        display: flex;
        flex-wrap: wrap;
        gap: var(--space-1);
    }

    .question-class-badge {
        display: inline-flex;
        align-items: center;
        gap: 2px;
        padding: 2px 6px;
        background: var(--bg-base);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-sm);
        font-size: 0.7rem;
        color: var(--text-muted);
    }

    .question-classes-bar {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        padding: var(--space-2);
        background: var(--bg-base);
        border-radius: var(--radius-sm);
    }

    .question-classes-label {
        font-size: 0.75rem;
        color: var(--text-muted);
    }

    /* ============================================
       COGNITIVE COVERAGE DISPLAY
       ============================================ */
    .cognitive-coverage {
        padding: var(--space-3);
        background: var(--bg-elevated);
        border-radius: var(--radius-md);
        border: 1px solid var(--border-subtle);
    }

    .coverage-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--space-2);
    }

    .coverage-bars {
        display: flex;
        flex-direction: column;
        gap: var(--space-2);
    }

    .coverage-bar {
        display: flex;
        align-items: center;
        gap: var(--space-2);
    }

    .coverage-bar-label {
        font-size: 0.75rem;
        color: var(--text-muted);
        width: 80px;
        flex-shrink: 0;
    }

    .coverage-bar-track {
        flex: 1;
        height: 6px;
        background: var(--border-light);
        border-radius: 3px;
        overflow: hidden;
    }

    .coverage-bar-fill {
        height: 100%;
        background: var(--accent);
        border-radius: 3px;
        transition: width 0.3s ease;
    }

    .coverage-percent {
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--text-secondary);
        width: 40px;
        text-align: right;
    }

    /* ============================================
       TEMPLATE INDICATOR
       ============================================ */
    .template-indicator {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        padding: var(--space-2) var(--space-3);
        background: var(--secondary-lighter);
        border-radius: var(--radius-sm);
        font-size: 0.8rem;
        color: var(--secondary);
    }

    .template-indicator-icon {
        font-size: 0.9rem;
    }

    .template-indicator-name {
        font-weight: 600;
    }

    /* ============================================
       CONCEPT EXTRACTION PANEL (P3)
       ============================================ */
    .extraction-panel {
        background: var(--bg-elevated);
        border-radius: var(--radius-md);
        border: 1px solid var(--border-subtle);
        padding: var(--space-4);
        display: flex;
        flex-direction: column;
        gap: var(--space-4);
    }

    .extraction-header {
        text-align: center;
    }

    .extraction-header h3 {
        font-family: var(--font-display);
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0 0 var(--space-2) 0;
    }

    .extraction-subtitle {
        font-size: 0.9rem;
        color: var(--text-muted);
        margin: 0;
    }

    .extraction-section {
        padding: var(--space-3);
        background: var(--bg-base);
        border-radius: var(--radius-sm);
    }

    .extraction-section h4 {
        font-family: var(--font-display);
        font-size: 0.95rem;
        font-weight: 600;
        color: var(--text-secondary);
        margin: 0 0 var(--space-2) 0;
    }

    .insights-list,
    .questions-list {
        margin: 0;
        padding-left: var(--space-4);
    }

    .insights-list li,
    .questions-list li {
        margin-bottom: var(--space-1);
        color: var(--text-primary);
        font-size: 0.9rem;
        line-height: 1.5;
    }

    .entity-selection-grid {
        display: flex;
        flex-wrap: wrap;
        gap: var(--space-2);
    }

    .entity-checkbox {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        padding: var(--space-2) var(--space-3);
        background: var(--bg-elevated);
        border: 2px solid var(--border-light);
        border-radius: var(--radius-sm);
        cursor: pointer;
        transition: all 0.15s ease;
    }

    .entity-checkbox:hover {
        border-color: var(--accent);
    }

    .entity-checkbox.selected {
        border-color: var(--accent);
        background: var(--accent-lighter);
    }

    .entity-checkbox input {
        accent-color: var(--accent);
    }

    .entity-name {
        font-size: 0.9rem;
        color: var(--text-primary);
    }

    .entity-badge {
        padding: 2px 6px;
        border-radius: var(--radius-sm);
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
    }

    .entity-badge.new {
        background: var(--secondary-light);
        color: var(--secondary);
    }

    .entity-badge.updated {
        background: var(--accent-light);
        color: var(--accent-dark);
    }

    .extraction-hint {
        font-size: 0.85rem;
        color: var(--text-muted);
        margin: 0 0 var(--space-2) 0;
    }

    .entity-row {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        width: 100%;
    }

    .entity-row .entity-checkbox {
        flex: 1;
    }

    .entity-advanced-btn {
        padding: var(--space-1) var(--space-2);
        background: transparent;
        border: 1px solid var(--border-light);
        border-radius: var(--radius-sm);
        color: var(--text-muted);
        font-size: 0.75rem;
        cursor: pointer;
        transition: all 0.15s ease;
        white-space: nowrap;
    }

    .entity-advanced-btn:hover {
        background: var(--accent-lighter);
        border-color: var(--accent);
        color: var(--accent);
    }

    .definition-hint {
        font-size: 0.85rem;
        color: var(--text-muted);
        margin: 0 0 var(--space-3) 0;
    }

    .definition-input-group {
        margin-bottom: var(--space-3);
    }

    .definition-input-group:last-child {
        margin-bottom: 0;
    }

    .definition-input-group label {
        display: block;
        font-weight: 600;
        font-size: 0.9rem;
        color: var(--text-secondary);
        margin-bottom: var(--space-1);
    }

    .definition-input-group textarea {
        width: 100%;
        padding: var(--space-2);
        border: 1px solid var(--border-medium);
        border-radius: var(--radius-sm);
        background: var(--bg-elevated);
        color: var(--text-primary);
        font-family: var(--font-body);
        font-size: 0.9rem;
        line-height: 1.5;
        resize: vertical;
    }

    .definition-input-group textarea:focus {
        outline: none;
        border-color: var(--accent);
        box-shadow: 0 0 0 3px var(--accent-lighter);
    }

    .definition-input-group textarea::placeholder {
        color: var(--text-subtle);
    }

    .extraction-actions {
        display: flex;
        justify-content: flex-end;
        gap: var(--space-3);
        padding-top: var(--space-2);
        border-top: 1px solid var(--border-subtle);
    }

    .extraction-actions button {
        padding: var(--space-2) var(--space-4);
        border-radius: var(--radius-sm);
        font-size: 0.95rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.15s ease;
    }

    .extraction-actions button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
</style>
