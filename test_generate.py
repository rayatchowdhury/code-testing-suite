"""
Test the AI generate functionality for stress tester.
"""
import asyncio
from ai.core.editor_ai import EditorAI

async def test_generate():
    print('Testing AI generate functionality...')
    ai = EditorAI()
    print(f'AI model: {ai.model is not None}')
    print(f'Generator docs loaded: {len(ai.generator_docs)} characters')
    print('Generator docs preview:', ai.generator_docs[:100] if ai.generator_docs else 'Empty')
    
    if ai.model:
        try:
            result = await ai.process_code('generate', '// test code', type='generator.cpp')
            print('Generate successful!')
            print('Result preview:', result[:200] if result else 'No result')
        except Exception as e:
            print(f'Generate failed: {e}')
            import traceback
            traceback.print_exc()
    else:
        print('No AI model available - check API key configuration')

if __name__ == "__main__":
    asyncio.run(test_generate())
