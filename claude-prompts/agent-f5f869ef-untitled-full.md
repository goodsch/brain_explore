# Claude Session Export

## Session Information

- **Session ID**: `agent-f5f869ef`
- **Export Mode**: Full Conversation
- **Total Messages**: 88 (39 user, 49 assistant)
- **First Message**: 12/1/2025, 1:44:55 PM
- **Last Message**: 12/1/2025, 1:50:43 PM
- **Project Path**: `/home/chris/dev/projects/codex/brain_explore`

---

## Conversation

### Assistant
> 12/1/2025, 1:44:55 PM

[
  {
    "type": "text",
    "text": "I'll help you research ADHD and autism dimensions from these books to inform the user profile system design. Let me start by locating the relevant ebooks."
  }
]

---

### Assistant
> 12/1/2025, 1:44:56 PM

[
  {
    "type": "tool_use",
    "id": "toolu_013hehzCMkHPZ5JieHbZdmCk",
    "name": "mcp__ebook-mcp__get_all_epub_files",
    "input": {
      "path": "/home/chris"
    }
  }
]

---

### Assistant
> 12/1/2025, 1:44:56 PM

[
  {
    "type": "tool_use",
    "id": "toolu_01Mo9VWRHse6qbwT7xPqzjYA",
    "name": "mcp__ebook-mcp__get_all_pdf_files",
    "input": {
      "path": "/home/chris"
    }
  }
]

---

### User
> 12/1/2025, 1:44:56 PM

[
  {
    "tool_use_id": "toolu_013hehzCMkHPZ5JieHbZdmCk",
    "type": "tool_result",
    "content": []
  }
]

---

### User
> 12/1/2025, 1:44:56 PM

[
  {
    "tool_use_id": "toolu_01Mo9VWRHse6qbwT7xPqzjYA",
    "type": "tool_result",
    "content": []
  }
]

---

### Assistant
> 12/1/2025, 1:45:00 PM

[
  {
    "type": "text",
    "text": "Let me try a more specific search in common ebook directories:"
  }
]

---

### Assistant
> 12/1/2025, 1:45:02 PM

[
  {
    "type": "tool_use",
    "id": "toolu_01LCdzvbvCHuN8mNVAZyBMCz",
    "name": "Bash",
    "input": {
      "command": "find /home/chris -type f \\( -name \"*Barkley*\" -o -name \"*Taking*Charge*\" -o -name \"*Unmasking*Autism*\" -o -name \"*Devon*Price*\" \\) 2>/dev/null | head -20",
      "description": "Search for Barkley and Price ebooks"
    }
  }
]

---

### User
> 12/1/2025, 1:47:03 PM

[
  {
    "tool_use_id": "toolu_01LCdzvbvCHuN8mNVAZyBMCz",
    "type": "tool_result",
    "content": "Command running in background with ID: 465bc5",
    "is_error": false
  }
]

---

### Assistant
> 12/1/2025, 1:47:07 PM

[
  {
    "type": "tool_use",
    "id": "toolu_012xEUrFajtqTJQbBE5ySMGA",
    "name": "BashOutput",
    "input": {
      "bash_id": "465bc5"
    }
  }
]

---

### User
> 12/1/2025, 1:47:07 PM

[
  {
    "tool_use_id": "toolu_012xEUrFajtqTJQbBE5ySMGA",
    "type": "tool_result",
    "content": "<status>running</status>\n\n<timestamp>2025-12-01T18:47:07.811Z</timestamp>"
  }
]

---

### Assistant
> 12/1/2025, 1:47:10 PM

[
  {
    "type": "tool_use",
    "id": "toolu_016ZBheBjCdJAy2u5aPAKKna",
    "name": "BashOutput",
    "input": {
      "bash_id": "465bc5"
    }
  }
]

---

### User
> 12/1/2025, 1:47:10 PM

[
  {
    "tool_use_id": "toolu_016ZBheBjCdJAy2u5aPAKKna",
    "type": "tool_result",
    "content": "<status>running</status>\n\n<timestamp>2025-12-01T18:47:10.751Z</timestamp>"
  }
]

---

### Assistant
> 12/1/2025, 1:47:13 PM

[
  {
    "type": "tool_use",
    "id": "toolu_018A23S5UZXtMDzQWHYWL1bq",
    "name": "BashOutput",
    "input": {
      "bash_id": "465bc5"
    }
  }
]

---

### User
> 12/1/2025, 1:47:13 PM

[
  {
    "tool_use_id": "toolu_018A23S5UZXtMDzQWHYWL1bq",
    "type": "tool_result",
    "content": "<status>running</status>\n\n<timestamp>2025-12-01T18:47:13.838Z</timestamp>"
  }
]

---

### Assistant
> 12/1/2025, 1:47:16 PM

[
  {
    "type": "tool_use",
    "id": "toolu_01BmAuxXG2HqvRXHC5J7K4BX",
    "name": "BashOutput",
    "input": {
      "bash_id": "465bc5"
    }
  }
]

---

### User
> 12/1/2025, 1:47:16 PM

[
  {
    "tool_use_id": "toolu_01BmAuxXG2HqvRXHC5J7K4BX",
    "type": "tool_result",
    "content": "<status>running</status>\n\n<timestamp>2025-12-01T18:47:16.712Z</timestamp>"
  }
]

---

### Assistant
> 12/1/2025, 1:47:19 PM

[
  {
    "type": "tool_use",
    "id": "toolu_012LFTuaYePa3XgwAhKo6x1C",
    "name": "BashOutput",
    "input": {
      "bash_id": "465bc5"
    }
  }
]

---

### User
> 12/1/2025, 1:47:19 PM

[
  {
    "tool_use_id": "toolu_012LFTuaYePa3XgwAhKo6x1C",
    "type": "tool_result",
    "content": "<status>running</status>\n\n<timestamp>2025-12-01T18:47:19.630Z</timestamp>"
  }
]

---

### Assistant
> 12/1/2025, 1:47:23 PM

[
  {
    "type": "text",
    "text": "Let me kill this search and try a different approach:"
  }
]

---

### Assistant
> 12/1/2025, 1:47:23 PM

[
  {
    "type": "tool_use",
    "id": "toolu_01QVAY2GetKBxmoqns5PuH6D",
    "name": "KillShell",
    "input": {
      "shell_id": "465bc5"
    }
  }
]

---

### User
> 12/1/2025, 1:47:23 PM

[
  {
    "tool_use_id": "toolu_01QVAY2GetKBxmoqns5PuH6D",
    "type": "tool_result",
    "content": "{\"message\":\"Successfully killed shell: 465bc5 (find /home/chris -type f \\\\( -name \\\"*Barkley*\\\" -o -name \\\"*Taking*Charge*\\\" -o -name \\\"*Unmasking*Autism*\\\" -o -name \\\"*Devon*Price*\\\" \\\\) 2>/dev/null | head -20)\",\"shell_id\":\"465bc5\"}"
  }
]

---

### Assistant
> 12/1/2025, 1:47:27 PM

[
  {
    "type": "tool_use",
    "id": "toolu_01AywSCFo36oceAHKdx9uxuD",
    "name": "mcp__ebook-mcp__get_all_epub_files",
    "input": {
      "path": "/home/chris/Documents"
    }
  }
]

---

### Assistant
> 12/1/2025, 1:47:28 PM

[
  {
    "type": "tool_use",
    "id": "toolu_0154bG9fkKsyi7GWragfcnr8",
    "name": "mcp__ebook-mcp__get_all_pdf_files",
    "input": {
      "path": "/home/chris/Documents"
    }
  }
]

---

### Assistant
> 12/1/2025, 1:47:28 PM

[
  {
    "type": "tool_use",
    "id": "toolu_01UoXmde9rGy4grBqbNbVBKB",
    "name": "mcp__ebook-mcp__get_all_epub_files",
    "input": {
      "path": "/home/chris/Downloads"
    }
  }
]

---

### Assistant
> 12/1/2025, 1:47:28 PM

[
  {
    "type": "tool_use",
    "id": "toolu_0169cCJ6SfktFqH8DjeVVLT2",
    "name": "mcp__ebook-mcp__get_all_pdf_files",
    "input": {
      "path": "/home/chris/Downloads"
    }
  }
]

---

### User
> 12/1/2025, 1:47:28 PM

[
  {
    "tool_use_id": "toolu_01AywSCFo36oceAHKdx9uxuD",
    "type": "tool_result",
    "content": []
  }
]

---

### User
> 12/1/2025, 1:47:29 PM

[
  {
    "tool_use_id": "toolu_0154bG9fkKsyi7GWragfcnr8",
    "type": "tool_result",
    "content": []
  }
]

---

### User
> 12/1/2025, 1:47:29 PM

[
  {
    "tool_use_id": "toolu_01UoXmde9rGy4grBqbNbVBKB",
    "type": "tool_result",
    "content": []
  }
]

---

### User
> 12/1/2025, 1:47:29 PM

[
  {
    "tool_use_id": "toolu_0169cCJ6SfktFqH8DjeVVLT2",
    "type": "tool_result",
    "content": []
  }
]

---

### Assistant
> 12/1/2025, 1:47:36 PM

[
  {
    "type": "tool_use",
    "id": "toolu_019jaEbxHp47KAr4hQ8Sdnpp",
    "name": "TodoWrite",
    "input": {
      "todos": [
        {
          "content": "Locate Barkley and Price ebooks in filesystem",
          "status": "in_progress",
          "activeForm": "Locating Barkley and Price ebooks in filesystem"
        },
        {
          "content": "Extract table of contents from both books",
          "status": "pending",
          "activeForm": "Extracting table of contents from both books"
        },
        {
          "content": "Read relevant chapters on ADHD dimensions and assessment",
          "status": "pending",
          "activeForm": "Reading relevant chapters on ADHD dimensions and assessment"
        },
        {
          "content": "Read relevant chapters on individual variation and profiles",
          "status": "pending",
          "activeForm": "Reading relevant chapters on individual variation and profiles"
        },
        {
          "content": "Synthesize findings into structured profile dimensions",
          "status": "pending",
          "activeForm": "Synthesizing findings into structured profile dimensions"
        }
      ]
    }
  }
]

---

### User
> 12/1/2025, 1:47:36 PM

[
  {
    "tool_use_id": "toolu_019jaEbxHp47KAr4hQ8Sdnpp",
    "type": "tool_result",
    "content": "Todos have been modified successfully. Ensure that you continue to use the todo list to track your progress. Please proceed with the current tasks if applicable"
  }
]

---

### Assistant
> 12/1/2025, 1:47:40 PM

[
  {
    "type": "tool_use",
    "id": "toolu_017xpx7f3JhcSdkCY6jtXmyk",
    "name": "Bash",
    "input": {
      "command": "ls -la /home/chris/Books 2>/dev/null | head -20",
      "description": "Check Books directory"
    }
  }
]

---

### Assistant
> 12/1/2025, 1:47:41 PM

[
  {
    "type": "tool_use",
    "id": "toolu_019eBTDNkQDDqeCVFbiw8pxS",
    "name": "Bash",
    "input": {
      "command": "ls -la /home/chris/ebooks 2>/dev/null | head -20",
      "description": "Check ebooks directory"
    }
  }
]

---

### Assistant
> 12/1/2025, 1:47:41 PM

[
  {
    "type": "tool_use",
    "id": "toolu_01QDTDPD1o4c4gQW4TZC1VX6",
    "name": "Bash",
    "input": {
      "command": "ls -la /home/chris/Library 2>/dev/null | head -20",
      "description": "Check Library directory"
    }
  }
]

---

### User
> 12/1/2025, 1:47:42 PM

[
  {
    "tool_use_id": "toolu_019eBTDNkQDDqeCVFbiw8pxS",
    "type": "tool_result",
    "content": "",
    "is_error": false
  }
]

---

### User
> 12/1/2025, 1:47:42 PM

[
  {
    "tool_use_id": "toolu_017xpx7f3JhcSdkCY6jtXmyk",
    "type": "tool_result",
    "content": "",
    "is_error": false
  }
]

---

### User
> 12/1/2025, 1:47:42 PM

[
  {
    "tool_use_id": "toolu_01QDTDPD1o4c4gQW4TZC1VX6",
    "type": "tool_result",
    "content": "total 20\ndrwxrwxr-x   3 chris chris  4096 Apr 29  2025 .\ndrwxr-xr-x 101 chris chris 12288 Dec  1 13:47 ..\ndrwxrwxr-x   3 chris chris  4096 Apr 29  2025 Application Support",
    "is_error": false
  }
]

---

### Assistant
> 12/1/2025, 1:47:46 PM

[
  {
    "type": "tool_use",
    "id": "toolu_01Ju43ntxaRhtZ6ACXWUXGdg",
    "name": "mcp__annas__search",
    "input": {
      "term": "Taking Charge of Adult ADHD Barkley"
    }
  }
]

---

### Assistant
> 12/1/2025, 1:47:47 PM

[
  {
    "type": "tool_use",
    "id": "toolu_018FspLCBQDdaND9FppuEjM8",
    "name": "mcp__annas__search",
    "input": {
      "term": "Unmasking Autism Devon Price"
    }
  }
]

---

### User
> 12/1/2025, 1:47:48 PM

[
  {
    "tool_use_id": "toolu_01Ju43ntxaRhtZ6ACXWUXGdg",
    "type": "tool_result",
    "content": [
      {
        "type": "text",
        "text": "Title: Taking Charge of Adult ADHD\nAuthors: Russell A. Barkley [Barkley, Russell A.]\nPublisher: \nLanguage: English [en]\nFormat: EPUB\nSize: 0.4MB\nURL: https://annas-archive.org/md5/4b13c64817fd9a8d4f4661d69257aae8\nHash: 4b13c64817fd9a8d4f4661d69257aae8\n\nTitle: Taking Charge of Adult ADHD, Second Edition: Proven Strategies to Succeed at Work, at Home, and in Relationships\nAuthors: Russell A. Barkley; Christine M. Benton\nPublisher: The Guilford Press, a division of Guildford Publications, Inc, 2, 2021\nLanguage: English [en]\nFormat: EPUB\nSize: 1.6MB\nURL: https://annas-archive.org/md5/46749127eea3d478f9f0c87ccf217363\nHash: 46749127eea3d478f9f0c87ccf217363\n\nTitle: Taking Charge of Adult ADHD\nAuthors: Russell A. Barkley\nPublisher: Guilford Publications, 2010\nLanguage: English [en]\nFormat: EPUB\nSize: 3.2MB\nURL: https://annas-archive.org/md5/9b12a9353a3260673f473c8c24bde0ed\nHash: 9b12a9353a3260673f473c8c24bde0ed\n\nTitle: Taking Charge of Adult ADHD\nAuthors: Russell A. barkley\nPublisher: The Guilford Press\nLanguage: English [en]\nFormat: EPUB\nSize: 2.5MB\nURL: https://annas-archive.org/md5/fddd69957fe3176ffaa58ccda5b99516\nHash: fddd69957fe3176ffaa58ccda5b99516\n\nTitle: Taking Charge of Adult ADHD\nAuthors: Russell A. Barkley, Christine M. Benton\nPublisher: Guilford Publications, Inc., New York, 2011\nLanguage: English [en]\nFormat: EPUB\nSize: 3.4MB\nURL: https://annas-archive.org/md5/75eb6cd9d51c27d18e4f5d5feebab333\nHash: 75eb6cd9d51c27d18e4f5d5feebab333\n\nTitle: Taking Charge of Adult ADHD, Second Edition: Proven Strategies to Succeed at Work, at Home, and in Relationships\nAuthors: Unknown\nPublisher: The Guilford Press, Second edition, New York, NY, 2022\nLanguage: English [en]\nFormat: EPUB\nSize: 2.5MB\nURL: https://annas-archive.org/md5/780db847f5f08d08e561b11a1b8195f1\nHash: 780db847f5f08d08e561b11a1b8195f1\n\nTitle: Taking Charge of Adult ADHD\nAuthors: Russell A. Barkley, Christine M. Benton\nPublisher: The Guilford Press, Guilford Publications Inc., New York, 2010\nLanguage: English [en]\nFormat: EPUB\nSize: 2.7MB\nURL: https://annas-archive.org/md5/d455d2ab347255d0f9d8d407b29a9b97\nHash: d455d2ab347255d0f9d8d407b29a9b97\n\nTitle: Taking charge of ADHD : the complete, authoritative guide for parents\nAuthors: Barkley, Russell A.\nPublisher: Guilford Publications, Inc., 3, 20130418\nLanguage: English [en]\nFormat: EPUB\nSize: 1.6MB\nURL: https://annas-archive.org/md5/046fee7d9237b7d2a8ec167babcafbd2\nHash: 046fee7d9237b7d2a8ec167babcafbd2\n\nTitle: Taking Charge of ADHD, Third Edition : The Complete, Authoritative Guide for Parents\nAuthors: Russell A. Barkley [Barkley, Russell A.]\nPublisher: Guilford Publications, Incorporated, 3rd, 2013-04-15\nLanguage: English [en]\nFormat: EPUB\nSize: 1.6MB\nURL: https://annas-archive.org/md5/d210afd2d3902261ac9856a1c7918870\nHash: d210afd2d3902261ac9856a1c7918870\n\nTitle: The Silent Struggle: Taking Charge of ADHD in Adults, The Complete Guide to Accept Yourself, Embrace Neurodiversity, Master Your Moods, Improve Relationships, Stay Organized, and Succeed in Life\nAuthors: L. William  Ross-Child  M.L.C.\nPublisher: Nova Mundo Publishing, Ltd, United Kingdom, 2022\nLanguage: English [en]\nFormat: EPUB\nSize: 1.6MB\nURL: https://annas-archive.org/md5/cc8e2ef7de48efae1cf871ec186487c5\nHash: cc8e2ef7de48efae1cf871ec186487c5\n\nTitle: When an Adult You Love Has ADHD : Professional Advice for Parents, Partners, and Siblings\nAuthors: Barkley, Russell A.\nPublisher: APA LifeTools, Washington, DC, 2016\nLanguage: English [en]\nFormat: EPUB\nSize: 1.4MB\nURL: https://annas-archive.org/md5/0396d11e88072565b6b1f913d8dc1ffc\nHash: 0396d11e88072565b6b1f913d8dc1ffc\n\nTitle: When an Adult You Love Has ADHD: Professional Advice for Parents, Partners, and Siblings (APA LifeTools Series)\nAuthors: Russell A. Barkley, PhD\nPublisher: American Psychological Association (APA), APA LifeTools, 2016\nLanguage: English [en]\nFormat: EPUB\nSize: 1.4MB\nURL: https://annas-archive.org/md5/bb0f53d50525537c9845405e2979ab48\nHash: bb0f53d50525537c9845405e2979ab48\n\nTitle: Vencendo o Transtorno de Déficit de Atenção/ Hiperatividade Adulto (Em Portuguese do Brasil)\nAuthors: Russell A. Barkley\nPublisher: Artmed, 1°, 2011\nLanguage: English [en]\nFormat: Portuguese [pt]\nSize: EPUB\nURL: https://annas-archive.org/md5/63487140427ec51ab1d1c71a11bd7a94\nHash: 63487140427ec51ab1d1c71a11bd7a94\n\nTitle: Taking Charge of Adult ADHD, Second Edition: Proven Strategies to Succeed at Work, at Home, and in Relationships\nAuthors: Russell A. Barkley; Christine M. Benton\nPublisher: The Guilford Press, a division of Guildford Publications, Inc, Second, 2021\nLanguage: English [en]\nFormat: MOBI\nSize: 1.0MB\nURL: https://annas-archive.org/md5/a99cf8a26f4cba183a93c4547f9094a2\nHash: a99cf8a26f4cba183a93c4547f9094a2\n\nTitle: Taking Charge of Adult ADHD\nAuthors: Russel A. Barkley, Christine M. Benton\nPublisher: The Guilford Press, 1, 2011\nLanguage: English [en]\nFormat: Portuguese [pt]\nSize: PDF\nURL: https://annas-archive.org/md5/23d71f17d124bc124b42734f4365056f\nHash: 23d71f17d124bc124b42734f4365056f\n\nTitle: Vencendo o TDAH Adulto\nAuthors: Russell A. Barkley, Christine M. Benton\nPublisher: Artmed, 1, 2011\nLanguage: English [en]\nFormat: Portuguese [pt]\nSize: AZW3\nURL: https://annas-archive.org/md5/e02ba4891507cdafe7e1b61c709a0ee7\nHash: e02ba4891507cdafe7e1b61c709a0ee7\n\nTitle: Oui-Oui et la girafe rose\nAuthors: Blyton, Enid\nPublisher: Hachette jeunesse - Disney, Oui-Oui 28, 1974\nLanguage: \nFormat: \nSize: \nURL: https://annas-archive.org/md5/dc9b2020a2fbf604c48c6a8b9c9141d9\nHash: dc9b2020a2fbf604c48c6a8b9c9141d9\n\nTitle: Taking Charge of Adult ADHD, Second Edition: Proven Strategies to Succeed at Work, at Home, and in Relationships\nAuthors: Russell A. Barkley, Christine M. Benton\nPublisher: The Guilford Press, a division of Guildford Publications, Inc, 2, 2021\nLanguage: English [en]\nFormat: AZW3\nSize: 2.0MB\nURL: https://annas-archive.org/md5/0a3e44c6a3522cf456219a3376ce7a5f\nHash: 0a3e44c6a3522cf456219a3376ce7a5f\n\nTitle: Taking Charge of ADHD ( Google Translate Version )\nAuthors: Russell A. Barkley\nPublisher: Guilford Publications, Inc., 3, 20130418\nLanguage: English [en]\nFormat: Chinese [zh]\nSize: EPUB\nURL: https://annas-archive.org/md5/617cde2b13ea218c20444368d2b816a1\nHash: 617cde2b13ea218c20444368d2b816a1\n\nTitle: Taking Charge of Adult ADHD, Second Edition: Proven Strategies to Succeed at Work, at Home, and in Relationships\nAuthors: Russell A. Barkley; Christine M. Benton\nPublisher: The Guilford Press, a division of Guildford Publications, Inc, Second, 2021\nLanguage: English [en]\nFormat: PDF\nSize: 3.4MB\nURL: https://annas-archive.org/md5/e8de5157de3160b5f714b629d7b02415\nHash: e8de5157de3160b5f714b629d7b02415\n\nTitle: Taking Charge of ADHD, Revised Edition: The Complete, Authoritative Guide for Parents\nAuthors: Russell A. Barkley PhD  ABPP  ABCN\nPublisher: The Guilford Press, revised edition, 2005;2000\nLanguage: English [en]\nFormat: PDF\nSize: 1.5MB\nURL: https://annas-archive.org/md5/eae28b5d468f9a47ae89eb6aa3d24df2\nHash: eae28b5d468f9a47ae89eb6aa3d24df2\n\nTitle: The Silent Struggle: Taking Charge of ADHD in Adults, The Complete Guide to Accept Yourself, Embrace Neurodiversity, Master Your Moods, Improve Relationships, Stay Organized, and Succeed in Life\nAuthors: L. William Ross-Child  M.L.C.\nPublisher: Nova Mundo Publishing, Ltd, United Kingdom, 2022\nLanguage: English [en]\nFormat: PDF\nSize: 3.2MB\nURL: https://annas-archive.org/md5/1d1f7e055760eca76ac0276efaf2cb12\nHash: 1d1f7e055760eca76ac0276efaf2cb12\n\nTitle: Take charge of ADHD : the complete authoritative guide for parents\nAuthors: Russell A Barkley\nPublisher: Hinkler Books Pty, Limited, Dingley VC, Unknown, September 2002\nLanguage: English [en]\nFormat: PDF\nSize: 16.6MB\nURL: https://annas-archive.org/md5/e00060a5fa41f888600dc76366d49115\nHash: e00060a5fa41f888600dc76366d49115\n\nTitle: Taking Charge of Adult ADHD\nAuthors: Barkley, Russell A.\nPublisher: Guilford Press, 2, 20110404\nLanguage: English [en]\nFormat: PDF\nSize: 2.1MB\nURL: https://annas-archive.org/md5/48d64890045d9be62d5a828098be8bf0\nHash: 48d64890045d9be62d5a828098be8bf0\n\nTitle: When an Adult You Love Has ADHD: Professional Advice for Parents, Partners, and Siblings\nAuthors: Barkley, Russell A.\nPublisher: 2016\nLanguage: English [en]\nFormat: AZW3\nSize: 1.7MB\nURL: https://annas-archive.org/md5/eb65d1de0a498ba4e2c427046e9ef0a3\nHash: eb65d1de0a498ba4e2c427046e9ef0a3\n\nTitle: Taking Charge of ADHD, Revised Edition: The Complete, Authoritative Guide for Parents\nAuthors: Barkley, Russell A., 1949-\nPublisher: Guilford Publications, Guilford Publications Inc., New York, 2005\nLanguage: English [en]\nFormat: PDF\nSize: 54.7MB\nURL: https://annas-archive.org/md5/6534f1cb6d8ae6b86921f6faa0e87d8b\nHash: 6534f1cb6d8ae6b86921f6faa0e87d8b\n\nTitle: Taking Charge of ADHD, Third Edition : The Complete, Authoritative Guide for Parents\nAuthors: Russell A. Barkley\nPublisher: The Guilford Press, 3rd, 2013-04-14\nLanguage: English [en]\nFormat: PDF\nSize: 3.5MB\nURL: https://annas-archive.org/md5/52989e5ba20619913de88da1f3176135\nHash: 52989e5ba20619913de88da1f3176135\n\nTitle: Taking Charge of ADHD, Revised Edition: The Complete, Authoritative Guide for Parents\nAuthors: Russell A. Barkley\nPublisher: Guilford Publications, Revised, 2000\nLanguage: English [en]\nFormat: PDF\nSize: 1.3MB\nURL: https://annas-archive.org/md5/6d5c3a099603a0bc50bd25d438998785\nHash: 6d5c3a099603a0bc50bd25d438998785\n\nTitle: Taking Charge of Adult ADHD: Proven Strategies to Succeed at Work, at Home, and in Relationships, 2nd Ed\nAuthors: Russell A. Barkley, Christine M. Benton\nPublisher: The Guilford Press, a division of Guildford Publications, Inc, 2, 2021\nLanguage: English [en]\nFormat: PDF\nSize: 3.5MB\nURL: https://annas-archive.org/md5/2ebca9bef1e535878294ff0054e77e7a\nHash: 2ebca9bef1e535878294ff0054e77e7a\n\nTitle: ADHD & The Mind’s Playground – Uncut with Dr. Russell Barkley\nAuthors: Russell barkley\nPublisher: Big Brain Productions Inc, TotallyADD uncut inverviews, 2014\nLanguage: English [en]\nFormat: PDF\nSize: 6.0MB\nURL: https://annas-archive.org/md5/bbd52800440bc37d685514c4e509ff90\nHash: bbd52800440bc37d685514c4e509ff90\n\nTitle: Taking charge of ADHD : the complete, authoritative guide for parents\nAuthors: Barkley, Russell A.\nPublisher: The Guilford Press, New York, New York State, September 2002\nLanguage: English [en]\nFormat: PDF\nSize: 35.5MB\nURL: https://annas-archive.org/md5/083259ed5cc948b0d33606341a8cb3f8\nHash: 083259ed5cc948b0d33606341a8cb3f8\n\nTitle: Taking Charge of Adult ADHD\nAuthors: Russell A. Barkley\nPublisher: The Guilford Press, Guilford Publications Inc., New York, 2010\nLanguage: English [en]\nFormat: PDF\nSize: 14.0MB\nURL: https://annas-archive.org/md5/92cd799b1e7caa894ed6e880339175d1\nHash: 92cd799b1e7caa894ed6e880339175d1\n\nTitle: The 18 Principles of Managing a Child with ADHD\nAuthors: Russ Barkley\nPublisher: 2011\nLanguage: English [en]\nFormat: PDF\nSize: 0.3MB\nURL: https://annas-archive.org/md5/903bb707d2c5a5dfa049d381b9957af0\nHash: 903bb707d2c5a5dfa049d381b9957af0\n\nTitle: When an Adult You Love Has ADHD: Professional Advice for Parents, Partners, and Siblings\nAuthors: Barkley, Russell A.\nPublisher: \nLanguage: \nFormat: \nSize: \nURL: https://annas-archive.org/md5/32a0ebe4e13ba58bc4027754303dde3d\nHash: 32a0ebe4e13ba58bc4027754303dde3d\n\nTitle: Taking Charge of ADHD: The Complete, Authoritative Guide for Parents (Revised Edition)\nAuthors: Russell A. Barkley\nPublisher: The Guilford Press, Rev. ed., New York, New York State, September 2002\nLanguage: English [en]\nFormat: PDF\nSize: 22.5MB\nURL: https://annas-archive.org/md5/86ff3afd0fdec34a9de4437238d41925\nHash: 86ff3afd0fdec34a9de4437238d41925\n\nTitle: Taking Charge of ADHD, Third Edition : The Complete, Authoritative Guide for Parents\nAuthors: Russell A. Barkley\nPublisher: New York: The Guilford Press, Guilford Publications Inc., New York, 2013\nLanguage: English [en]\nFormat: PDF\nSize: 25.5MB\nURL: https://annas-archive.org/md5/47e8f914e46d625cd7fd4c28886589dd\nHash: 47e8f914e46d625cd7fd4c28886589dd\n\n"
      }
    ]
  }
]

---

### User
> 12/1/2025, 1:47:48 PM

[
  {
    "tool_use_id": "toolu_018FspLCBQDdaND9FppuEjM8",
    "type": "tool_result",
    "content": [
      {
        "type": "text",
        "text": "Title: Unmasking Autism: Discovering the New Faces of Neurodiversity\nAuthors: by Devon Price\nPublisher: Harmony Books, New York, USA, 2022-04-05\nLanguage: ✅ English [en]\nFormat: EPUB\nSize: 3.0MB\nURL: https://annas-archive.org/md5/f6b31a8dafd6bd39a5986833e66293e6\nHash: f6b31a8dafd6bd39a5986833e66293e6\n\nTitle: Unmasking Autism: Discovering the New Faces of Neurodiversity\nAuthors: by Devon Price\nPublisher: Harmony Books, New York, USA, 2022-04-05\nLanguage: ✅ English [en]\nFormat: EPUB\nSize: 3.0MB\nURL: https://annas-archive.org/md5/e567bf6c363319d7b82512db02959ff5\nHash: e567bf6c363319d7b82512db02959ff5\n\nTitle: Unmasking Autism : Discovering the New Faces of Neurodiversity\nAuthors: Devon  Price\nPublisher: Potter/Ten Speed/Harmony/Rodale, First edition, New York, 2022\nLanguage: English [en]\nFormat: EPUB\nSize: 3.0MB\nURL: https://annas-archive.org/md5/723eb4596742e4ae9db5cf7fb558abaf\nHash: 723eb4596742e4ae9db5cf7fb558abaf\n\nTitle: Unmasking for Life : The Autistic Person's Guide to Connecting, Loving, and Living Authentically\nAuthors: Devon Price, PhD\nPublisher: Harmony/Rodale/Convergent, 2025\nLanguage: English [en]\nFormat: EPUB\nSize: 2.1MB\nURL: https://annas-archive.org/md5/e166aee3b620f8d9872b3b364de8ef4b\nHash: e166aee3b620f8d9872b3b364de8ef4b\n\nTitle: Magic for a Price\nAuthors: Monk, Devon\nPublisher: Allie Beckstrom 9, 2012\nLanguage: English [en]\nFormat: EPUB\nSize: 1.2MB\nURL: https://annas-archive.org/md5/7641dcd0828efeff28bc5e441f44cbac\nHash: 7641dcd0828efeff28bc5e441f44cbac\n\nTitle: Magic for a Price\nAuthors: Devon Monk [Monk, Devon]\nPublisher: Roc, Allie Beckstrom Series #9, 2012\nLanguage: English [en]\nFormat: EPUB\nSize: 0.6MB\nURL: https://annas-archive.org/md5/3c623b684e584724f2de6ad4cdb3e227\nHash: 3c623b684e584724f2de6ad4cdb3e227\n\nTitle: Magic for a Price 9\nAuthors: Monk, Devon\nPublisher: Allie Beckstrom #9, 2012\nLanguage: English [en]\nFormat: EPUB\nSize: 1.2MB\nURL: https://annas-archive.org/md5/f7a0bc0f2cfd01f7cc6db2d54b2bea9a\nHash: f7a0bc0f2cfd01f7cc6db2d54b2bea9a\n\nTitle: Unlearning Shame : How We Can Reject Self-Blame Culture and Reclaim Our Power\nAuthors: Devon Price, PhD\nPublisher: Potter/Ten Speed/Harmony/Rodale, Penguin Random House LLC, New York, NY, 2024\nLanguage: English [en]\nFormat: EPUB\nSize: 6.5MB\nURL: https://annas-archive.org/md5/d671bd3535f0c10bfeff889c2336719c\nHash: d671bd3535f0c10bfeff889c2336719c\n\nTitle: 30 day Unmasking Journal for ADHD & Autism for self-discovery & accomodation\nAuthors: Usman, Ilham\nPublisher: UNKNOWN, 2023\nLanguage: English [en]\nFormat: EPUB\nSize: 2.8MB\nURL: https://annas-archive.org/md5/a15a8f5a9b87370ede5f3c58278cc4b4\nHash: a15a8f5a9b87370ede5f3c58278cc4b4\n\nTitle: Magic for a Price : An Allie Beckstrom Novel\nAuthors: Devon Monk\nPublisher: Penguin Publishing Group, Penguin Random House LLC, [N.p.], 2012\nLanguage: English [en]\nFormat: EPUB\nSize: 1.4MB\nURL: https://annas-archive.org/md5/35c4ac4dfff0bbd22881fcd70b7e62de\nHash: 35c4ac4dfff0bbd22881fcd70b7e62de\n\nTitle: Laziness does not exist : a defense of the exhausted, exploited, and overworked\nAuthors: Devon Price [Devon Price]\nPublisher: Atria Books, an imprint of Simon & Schuster, Inc, Simon & Schuster, New York, NY, 2021\nLanguage: English [en]\nFormat: EPUB\nSize: 3.0MB\nURL: https://annas-archive.org/md5/e707d220dc2f0879e91934cc402f22d6\nHash: e707d220dc2f0879e91934cc402f22d6\n\nTitle: Masked Deception: A MM Erotic Thriller Novella\nAuthors: Reyes, Ashley\nPublisher: Independent, 2024\nLanguage: English [en]\nFormat: EPUB\nSize: 0.7MB\nURL: https://annas-archive.org/md5/11675eb70557a5a11a8b0bf4de5cad79\nHash: 11675eb70557a5a11a8b0bf4de5cad79\n\nTitle: Unmasking a Duke\nAuthors: St Clair, Ellie\nPublisher: Prairie Lily Press\nLanguage: English [en]\nFormat: EPUB\nSize: 0.1MB\nURL: https://annas-archive.org/md5/57dcebcaf62b534f6b258fa566d9d4c2\nHash: 57dcebcaf62b534f6b258fa566d9d4c2\n\nTitle: Irresistible You (Unmasking Elena Montella)\nAuthors: Connelly, Victoria\nPublisher: Notting Hill Press, 2011\nLanguage: English [en]\nFormat: EPUB\nSize: 0.3MB\nURL: https://annas-archive.org/md5/dff1fa63c0b1f203a10ee8f5cbfbde25\nHash: dff1fa63c0b1f203a10ee8f5cbfbde25\n\nTitle: Allie Beckstrom 09 - Magic for a Price\nAuthors: Devon Monk\nPublisher: 2012\nLanguage: English [en]\nFormat: EPUB\nSize: 0.8MB\nURL: https://annas-archive.org/md5/722e000b87b5269d5efc07e225c083e0\nHash: 722e000b87b5269d5efc07e225c083e0\n\nTitle: Unmasking Her Fake Girlfriend: A Lesbian/Sapphic Romance\nAuthors: Raina Kaufman\nPublisher: Lesbian Bodyguard 5, 2023\nLanguage: English [en]\nFormat: EPUB\nSize: 0.7MB\nURL: https://annas-archive.org/md5/ae1c86edfd164a7ba58910378769ed51\nHash: ae1c86edfd164a7ba58910378769ed51\n\nTitle: Unmasking a Duke\nAuthors: St Clair, Ellie\nPublisher: Prairie Lily Press\nLanguage: English [en]\nFormat: EPUB\nSize: 0.1MB\nURL: https://annas-archive.org/md5/579757b87770809056bccf4942a8b52d\nHash: 579757b87770809056bccf4942a8b52d\n\nTitle: [Allie Beckstrom 09] • Magic for a Price\nAuthors: Monk, Devon\nPublisher: New American Library, Penguin Random House LLC, [N.p.], 2012\nLanguage: English [en]\nFormat: EPUB\nSize: 0.6MB\nURL: https://annas-archive.org/md5/82284d8ea67f1050ecc0659ef96e1b12\nHash: 82284d8ea67f1050ecc0659ef96e1b12\n\nTitle: Unmasking the Marquess\nAuthors: Jackson, K J\nPublisher: AWD Publishing, Hold Your Breath 2, 2014\nLanguage: English [en]\nFormat: EPUB\nSize: 0.3MB\nURL: https://annas-archive.org/md5/e38b9843ab1dd36a016854404cd495b8\nHash: e38b9843ab1dd36a016854404cd495b8\n\nTitle: Magic for a Price : An Allie Beckstrom Novel\nAuthors: Monk, Devon\nPublisher: Roc, Allie Beckstrom 9, 2012\nLanguage: English [en]\nFormat: RAR\nSize: 0.6MB\nURL: https://annas-archive.org/md5/377db8a886b5e6e830c2a87bfbaf3f38\nHash: 377db8a886b5e6e830c2a87bfbaf3f38\n\nTitle: Laziness does not exist : a defense of the exhausted, exploited, and overworked\nAuthors: Devon Price [Devon Price]\nPublisher: Atria Books, an imprint of Simon & Schuster, Inc, Simon & Schuster, New York, NY, 2021\nLanguage: English [en]\nFormat: PDF\nSize: 5.0MB\nURL: https://annas-archive.org/md5/10c275cacdfdf555a4c039869a2d33a6\nHash: 10c275cacdfdf555a4c039869a2d33a6\n\nTitle: Laziness does not exist : a defense of the exhausted, exploited, and overworked\nAuthors: Devon Price [Devon Price]\nPublisher: Atria Books, an imprint of Simon & Schuster, Inc, Simon & Schuster, New York, NY, 2021\nLanguage: English [en]\nFormat: PDF\nSize: 5.0MB\nURL: https://annas-archive.org/md5/25e4d640bbff7c81bdfeb6f16fb4d453\nHash: 25e4d640bbff7c81bdfeb6f16fb4d453\n\nTitle: Laziness does not exist : a defense of the exhausted, exploited, and overworked\nAuthors: Devon Price [Devon Price]\nPublisher: Atria Books, an imprint of Simon & Schuster, Inc, Simon & Schuster, New York, NY, 2021\nLanguage: English [en]\nFormat: LIT\nSize: 2.2MB\nURL: https://annas-archive.org/md5/a2d143dd2358af460ccaa1b680dd72df\nHash: a2d143dd2358af460ccaa1b680dd72df\n\nTitle: Laziness does not exist : a defense of the exhausted, exploited, and overworked\nAuthors: Devon Price [Devon Price]\nPublisher: Atria Books, an imprint of Simon & Schuster, Inc, Simon & Schuster, New York, NY, 2021\nLanguage: English [en]\nFormat: LIT\nSize: 2.2MB\nURL: https://annas-archive.org/md5/25a39c48b54fbfbbdcf3dcf60f9ced8e\nHash: 25a39c48b54fbfbbdcf3dcf60f9ced8e\n\nTitle: Magic for a Price: A Novel\nAuthors: Monk, Devon\nPublisher: Penguin Publishing Group, 2012\nLanguage: \nFormat: \nSize: \nURL: https://annas-archive.org/md5/9f94bc134e1c383fa6b6a0e43941b378\nHash: 9f94bc134e1c383fa6b6a0e43941b378\n\nTitle: Laziness does not exist : a defense of the exhausted, exploited, and overworked\nAuthors: Devon Price [Devon Price]\nPublisher: Atria Books, an imprint of Simon & Schuster, Inc, Simon & Schuster, New York, NY, 2021\nLanguage: English [en]\nFormat: LIT\nSize: 2.2MB\nURL: https://annas-archive.org/md5/51c8f31bd4a362d1e5a6c8c5a3eb8c72\nHash: 51c8f31bd4a362d1e5a6c8c5a3eb8c72\n\nTitle: Christie's wine companion\nAuthors: INTRO. MICHAEL BROADBENT ED. PAMELA VANDYKE PRICE\nPublisher: Webb & Bower (Publishers) Ltd, New ed, Exeter, Devon, London, 1989\nLanguage: English [en]\nFormat: PDF\nSize: 13.0MB\nURL: https://annas-archive.org/md5/c054ac2601276857d17bd34405fd5f4d\nHash: c054ac2601276857d17bd34405fd5f4d\n\nTitle: Allie Beckstrom 09 - Magic for a Price\nAuthors: Devon Monk\nPublisher: 2012\nLanguage: English [en]\nFormat: PDF\nSize: 1.2MB\nURL: https://annas-archive.org/md5/4d17349b53b917987906e63d67af44fa\nHash: 4d17349b53b917987906e63d67af44fa\n\nTitle: Unmasking autism : discovering the new faces of neurodiversity\nAuthors: Devon Price, PhD\nPublisher: Potter/Ten Speed/Harmony/Rodale, First edition, New York, 2022\nLanguage: English [en]\nFormat: PDF\nSize: 15.3MB\nURL: https://annas-archive.org/md5/edf463e91eacfe199e5d49b59054cf45\nHash: edf463e91eacfe199e5d49b59054cf45\n\nTitle: Irresistible You (Unmasking Elena Montella)\nAuthors: Connelly, Victoria\nPublisher: Notting Hill Press, 2014\nLanguage: English [en]\nFormat: AZW3\nSize: 0.4MB\nURL: https://annas-archive.org/md5/3f6039645c910c8ee7b24baaa62d5145\nHash: 3f6039645c910c8ee7b24baaa62d5145\n\nTitle: Unmasking Autism\nAuthors: Price, Devon\nPublisher: Harmony/Rodale, 2022\nLanguage: English [en]\nFormat: AZW3\nSize: 1.7MB\nURL: https://annas-archive.org/md5/120fab19c6be4768b7199671a4e5599c\nHash: 120fab19c6be4768b7199671a4e5599c\n\nTitle: Laziness does not exist : a defense of the exhausted, exploited, and overworked\nAuthors: Devon Price; OverDrive, Inc\nPublisher: Atria Books, an imprint of Simon & Schuster, Inc, Simon & Schuster, New York, NY, 2021\nLanguage: English [en]\nFormat: PDF\nSize: 5.0MB\nURL: https://annas-archive.org/md5/40190c52e5f9360adcafe2ebe6bf641f\nHash: 40190c52e5f9360adcafe2ebe6bf641f\n\nTitle: Unmasking Elena Montella\nAuthors: Connelly, Victoria\nPublisher: 2014\nLanguage: English [en]\nFormat: AZW3\nSize: 0.5MB\nURL: https://annas-archive.org/md5/1ca129257df6e533e5214e03f6bafb1a\nHash: 1ca129257df6e533e5214e03f6bafb1a\n\nTitle: Unmasking Elena Montella\nAuthors: Connelly, Victoria\nPublisher: Notting Hill Press, 2011\nLanguage: English [en]\nFormat: MOBI\nSize: 0.5MB\nURL: https://annas-archive.org/md5/5e77389f4c27ca7610ab5212004f0a5a\nHash: 5e77389f4c27ca7610ab5212004f0a5a\n\nTitle: Magic for a Price: A Novel\nAuthors: \nPublisher: Roc, 2012\nLanguage: \nFormat: \nSize: \nURL: https://annas-archive.org/md5/98897bfb2cc3a740ee1184f5532fa1fd\nHash: 98897bfb2cc3a740ee1184f5532fa1fd\n\nTitle: The Unmasking\nAuthors: Burkhead, David\nPublisher: Dhampyre the Hunter 1, 2018\nLanguage: \nFormat: \nSize: \nURL: https://annas-archive.org/md5/2b6e21586d47c31da763d0e7fd5696d4\nHash: 2b6e21586d47c31da763d0e7fd5696d4\n\nTitle: Unmasking for Life: The Autistic Person's Guide to Connecting, Loving, and Living Authentically\nAuthors: Devon Price, PhD\nPublisher: Harmony/Rodale/Convergent, 2025\nLanguage: English [en]\nFormat: PDF\nSize: 3.8MB\nURL: https://annas-archive.org/md5/84a81e9bb815551d9fa90619b3b7e7d7\nHash: 84a81e9bb815551d9fa90619b3b7e7d7\n\nTitle: Unmasking Autism : Discovering the New Faces of Neurodiversity\nAuthors: Devon  Price\nPublisher: Potter/Ten Speed/Harmony/Rodale, First edition, New York, 2022\nLanguage: English [en]\nFormat: MOBI\nSize: 2.0MB\nURL: https://annas-archive.org/md5/adb01dec7590a205171dcfd3f0e13533\nHash: adb01dec7590a205171dcfd3f0e13533\n\nTitle: Unmasking the Angel: Revealing the Spiritual Identity of a Local Congregation\nAuthors: Stephen Langford; Foreword by Ruth Gouldbourne\nPublisher: Wipf & Stock Publishers, First, 2025\nLanguage: \nFormat: \nSize: \nURL: https://annas-archive.org/md5/a89ff6371d424149812d05596e33a8ad\nHash: a89ff6371d424149812d05596e33a8ad\n\nTitle: Magic for a Price : An Allie Beckstrom Novel\nAuthors: Monk, Devon\nPublisher: Ace, Allie Beckstrom 9, 0\nLanguage: English [en]\nFormat: RAR\nSize: 0.5MB\nURL: https://annas-archive.org/md5/f2144da7049ff281404dffe96490803f\nHash: f2144da7049ff281404dffe96490803f\n\nTitle: Unmasking\nAuthors: Berg, Carol\nPublisher: Elemental Magic SS3, 0\nLanguage: English [en]\nFormat: RAR\nSize: 0.1MB\nURL: https://annas-archive.org/md5/ff88d0e1e254b5dbbce4a3fc68ff2fcb\nHash: ff88d0e1e254b5dbbce4a3fc68ff2fcb\n\nTitle: Magic for a Price\nAuthors: Monk, Devon\nPublisher: Allie Beckstrom 9, 2012\nLanguage: English [en]\nFormat: MOBI\nSize: 1.4MB\nURL: https://annas-archive.org/md5/387bb79a132048fe883182785e9b05b2\nHash: 387bb79a132048fe883182785e9b05b2\n\nTitle: Allie Beckstrom 09 - Magic for a Price\nAuthors: Devon Monk\nPublisher: 2012\nLanguage: English [en]\nFormat: MOBI\nSize: 0.5MB\nURL: https://annas-archive.org/md5/9726b32b675efb03a82ca086fcc0f9b2\nHash: 9726b32b675efb03a82ca086fcc0f9b2\n\nTitle: 自閉者的面具,為何戴上,如何卸下\nAuthors: 戴文.普萊斯(Devon Price);[譯]許雅淑,李宗義\nPublisher: 大家出版, 1, 1, 2025\nLanguage: \nFormat: \nSize: \nURL: https://annas-archive.org/md5/0d58c2a23267cbc7bbef36960e56a7cd\nHash: 0d58c2a23267cbc7bbef36960e56a7cd\n\n"
      }
    ]
  }
]

---

### Assistant
> 12/1/2025, 1:47:53 PM

[
  {
    "type": "text",
    "text": "Perfect! I found both books. Let me download the most recent editions:"
  }
]

---

### Assistant
> 12/1/2025, 1:47:55 PM

[
  {
    "type": "tool_use",
    "id": "toolu_015UGCD4S1Fa9srg7QqKYgfX",
    "name": "mcp__annas__download",
    "input": {
      "hash": "46749127eea3d478f9f0c87ccf217363",
      "title": "Taking Charge of Adult ADHD Second Edition",
      "format": "epub"
    }
  }
]

---

### Assistant
> 12/1/2025, 1:47:57 PM

[
  {
    "type": "tool_use",
    "id": "toolu_015xMqFrYuBKNjA2Dk2BfnoP",
    "name": "mcp__annas__download",
    "input": {
      "hash": "f6b31a8dafd6bd39a5986833e66293e6",
      "title": "Unmasking Autism",
      "format": "epub"
    }
  }
]

---

### User
> 12/1/2025, 1:48:05 PM

[
  {
    "tool_use_id": "toolu_015UGCD4S1Fa9srg7QqKYgfX",
    "type": "tool_result",
    "content": [
      {
        "type": "text",
        "text": "Book downloaded successfully to path: /home/chris/dev/projects/codex/brain_explore/books"
      }
    ]
  }
]

---

### User
> 12/1/2025, 1:48:06 PM

[
  {
    "tool_use_id": "toolu_015xMqFrYuBKNjA2Dk2BfnoP",
    "type": "tool_result",
    "content": [
      {
        "type": "text",
        "text": "Book downloaded successfully to path: /home/chris/dev/projects/codex/brain_explore/books"
      }
    ]
  }
]

---

### Assistant
> 12/1/2025, 1:48:12 PM

[
  {
    "type": "tool_use",
    "id": "toolu_012b79o1pdi4gNQqXh8LXA2y",
    "name": "TodoWrite",
    "input": {
      "todos": [
        {
          "content": "Locate Barkley and Price ebooks in filesystem",
          "status": "completed",
          "activeForm": "Locating Barkley and Price ebooks in filesystem"
        },
        {
          "content": "Extract table of contents from both books",
          "status": "in_progress",
          "activeForm": "Extracting table of contents from both books"
        },
        {
          "content": "Read relevant chapters on ADHD dimensions and assessment",
          "status": "pending",
          "activeForm": "Reading relevant chapters on ADHD dimensions and assessment"
        },
        {
          "content": "Read relevant chapters on individual variation and profiles",
          "status": "pending",
          "activeForm": "Reading relevant chapters on individual variation and profiles"
        },
        {
          "content": "Synthesize findings into structured profile dimensions",
          "status": "pending",
          "activeForm": "Synthesizing findings into structured profile dimensions"
        }
      ]
    }
  }
]

---

### User
> 12/1/2025, 1:48:12 PM

[
  {
    "tool_use_id": "toolu_012b79o1pdi4gNQqXh8LXA2y",
    "type": "tool_result",
    "content": "Todos have been modified successfully. Ensure that you continue to use the todo list to track your progress. Please proceed with the current tasks if applicable"
  }
]

---

### Assistant
> 12/1/2025, 1:48:16 PM

[
  {
    "type": "tool_use",
    "id": "toolu_01DvdZK6VXZSKVEMQPmEdSpz",
    "name": "mcp__ebook-mcp__get_all_epub_files",
    "input": {
      "path": "/home/chris/dev/projects/codex/brain_explore/books"
    }
  }
]

---

### User
> 12/1/2025, 1:48:16 PM

[
  {
    "tool_use_id": "toolu_01DvdZK6VXZSKVEMQPmEdSpz",
    "type": "tool_result",
    "content": [
      {
        "type": "text",
        "text": "Motivational Interviewing 4th Ed - Miller and Rollnick.epub"
      },
      {
        "type": "text",
        "text": "Highly Sensitive Person - Elaine Aron.epub"
      },
      {
        "type": "text",
        "text": "Internal Family Systems Therapy - Richard Schwartz.epub"
      },
      {
        "type": "text",
        "text": "Power of Character Strengths - Niemiec McGrath.epub"
      },
      {
        "type": "text",
        "text": "Learning ACT 2nd Ed - Luoma Hayes Walser.epub"
      },
      {
        "type": "text",
        "text": "A More Beautiful Question - Warren Berger.epub"
      },
      {
        "type": "text",
        "text": "Existential Psychotherapy - Irvin Yalom.epub"
      },
      {
        "type": "text",
        "text": "How Emotions Are Made - Lisa Feldman Barrett.epub"
      },
      {
        "type": "text",
        "text": "Taking Charge of Adult ADHD 2nd Ed - Barkley.epub"
      },
      {
        "type": "text",
        "text": "Executive Functions - Russell Barkley.epub"
      },
      {
        "type": "text",
        "text": "How We Learn - Benedict Carey.epub"
      },
      {
        "type": "text",
        "text": "The Innovators DNA - Dyer Gregersen Christensen.epub"
      },
      {
        "type": "text",
        "text": "Metaphors We Live By - Lakoff and Johnson.epub"
      },
      {
        "type": "text",
        "text": "Taking Charge of Adult ADHD Second Edition.epub"
      },
      {
        "type": "text",
        "text": "Developing Mind - Daniel Siegel.epub"
      },
      {
        "type": "text",
        "text": "Atlas of the Heart - Brene Brown.epub"
      },
      {
        "type": "text",
        "text": "Maps of Meaning - Jordan Peterson.epub"
      },
      {
        "type": "text",
        "text": "Mans Search for Meaning - Viktor Frankl.epub"
      },
      {
        "type": "text",
        "text": "Thinking Fast and Slow - Daniel Kahneman.epub"
      },
      {
        "type": "text",
        "text": "Art of Learning - Josh Waitzkin.epub"
      },
      {
        "type": "text",
        "text": "Humble Inquiry 2nd Ed - Edgar Schein.epub"
      },
      {
        "type": "text",
        "text": "The Extended Mind - Annie Murphy Paul.epub"
      },
      {
        "type": "text",
        "text": "The Body Keeps the Score - Bessel van der Kolk.epub"
      },
      {
        "type": "text",
        "text": "The Denial of Death - Ernest Becker.epub"
      },
      {
        "type": "text",
        "text": "Experiential Learning 2nd Ed - David Kolb.epub"
      },
      {
        "type": "text",
        "text": "Unmasking Autism - Devon Price.epub"
      },
      {
        "type": "text",
        "text": "The Developing Mind 3rd Ed - Daniel Siegel.epub"
      },
      {
        "type": "text",
        "text": "The Fifth Discipline - Peter Senge.epub"
      },
      {
        "type": "text",
        "text": "Unmasking Autism.epub"
      },
      {
        "type": "text",
        "text": "Being You - Anil Seth.epub"
      },
      {
        "type": "text",
        "text": "Surfing Uncertainty - Andy Clark.epub"
      },
      {
        "type": "text",
        "text": "Thinking in Systems - Donella Meadows.epub"
      },
      {
        "type": "text",
        "text": "Behave - Robert Sapolsky.epub"
      },
      {
        "type": "text",
        "text": "Handbook of Psychotherapy Integration 3rd Ed - Norcross Goldfried.epub"
      },
      {
        "type": "text",
        "text": "Self-Compassion - Kristin Neff.epub"
      },
      {
        "type": "text",
        "text": "The Design of Everyday Things - Don Norman.epub"
      },
      {
        "type": "text",
        "text": "A Mind for Numbers - Barbara Oakley.epub"
      }
    ]
  }
]

---

### Assistant
> 12/1/2025, 1:48:20 PM

[
  {
    "type": "tool_use",
    "id": "toolu_016h1YULd46ZUnqivbhYFFwA",
    "name": "mcp__ebook-mcp__get_epub_toc",
    "input": {
      "epub_path": "/home/chris/dev/projects/codex/brain_explore/books/Taking Charge of Adult ADHD Second Edition.epub"
    }
  }
]

---

### Assistant
> 12/1/2025, 1:48:21 PM

[
  {
    "type": "tool_use",
    "id": "toolu_01MvBcUWsDk3r5zf2mtThNkz",
    "name": "mcp__ebook-mcp__get_epub_toc",
    "input": {
      "epub_path": "/home/chris/dev/projects/codex/brain_explore/books/Unmasking Autism.epub"
    }
  }
]

---

### User
> 12/1/2025, 1:48:21 PM

[
  {
    "tool_use_id": "toolu_016h1YULd46ZUnqivbhYFFwA",
    "type": "tool_result",
    "content": [
      {
        "type": "text",
        "text": "Praise for Taking Charge of Adult ADHD"
      },
      {
        "type": "text",
        "text": "text/part0000.html#0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "Also from Russell A. Barkley"
      },
      {
        "type": "text",
        "text": "text/part0001.html#UGI0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "Title Page"
      },
      {
        "type": "text",
        "text": "text/part0002.html#1T140-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "Dedication"
      },
      {
        "type": "text",
        "text": "text/part0003.html#2RHM0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "Copyright Page"
      },
      {
        "type": "text",
        "text": "text/part0004.html#3Q280-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "Contents"
      },
      {
        "type": "text",
        "text": "text/part0005.html#4OIQ0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "Acknowledgments"
      },
      {
        "type": "text",
        "text": "text/part0006.html#5N3C0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "Author’s Note"
      },
      {
        "type": "text",
        "text": "text/part0007.html#6LJU0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "Introduction"
      },
      {
        "type": "text",
        "text": "text/part0008.html#7K4G0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "Step One: To Get Started, Get Evaluated"
      },
      {
        "type": "text",
        "text": "text/part0009_split_000.html#8IL20-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "1. Is It Possible That You Have ADHD?"
      },
      {
        "type": "text",
        "text": "text/part0010_split_000.html#9H5K0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "2. Can You Handle the Problem on Your Own?"
      },
      {
        "type": "text",
        "text": "text/part0011_split_000.html#AFM60-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "3. Where Can You Go to Get Help?"
      },
      {
        "type": "text",
        "text": "text/part0012_split_000.html#BE6O0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "4. What Do You Need for the Evaluation?"
      },
      {
        "type": "text",
        "text": "text/part0013_split_000.html#CCNA0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "5. What Will the Evaluation Tell You?"
      },
      {
        "type": "text",
        "text": "text/part0014_split_000.html#DB7S0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "Step Two: Change Your Mindset: Know and Own Your ADHD"
      },
      {
        "type": "text",
        "text": "text/part0015_split_000.html#E9OE0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "6. Know Your ADHD"
      },
      {
        "type": "text",
        "text": "text/part0016_split_000.html#F8900-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "7. Resisting Impulses: The First Step in Self-Control"
      },
      {
        "type": "text",
        "text": "text/part0017_split_000.html#G6PI0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "8. Self-Control:"
      },
      {
        "type": "text",
        "text": "text/part0018_split_000.html#H5A40-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "9. Executive Functions: The Seven Abilities That Make Up Self-Control … and More"
      },
      {
        "type": "text",
        "text": "text/part0019_split_000.html#I3QM0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "10. The Nature of ADHD and How You Can Master It"
      },
      {
        "type": "text",
        "text": "text/part0020_split_000.html#J2B80-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "11. Own Your ADHD"
      },
      {
        "type": "text",
        "text": "text/part0021_split_000.html#K0RQ0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "Step Three: Change Your Brain: Medications for Mastering ADHD"
      },
      {
        "type": "text",
        "text": "text/part0022_split_000.html#KVCC0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "12. Why It Makes Sense to Try Medication"
      },
      {
        "type": "text",
        "text": "text/part0023_split_000.html#LTSU0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "13. The Stimulants"
      },
      {
        "type": "text",
        "text": "text/part0024_split_000.html#MSDG0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "14. The Nonstimulants"
      },
      {
        "type": "text",
        "text": "text/part0025_split_000.html#NQU20-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "15. What to Expect from Treatment"
      },
      {
        "type": "text",
        "text": "text/part0026_split_000.html#OPEK0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "Step Four: Change Your Life: Everyday Rules for Success"
      },
      {
        "type": "text",
        "text": "text/part0027_split_000.html#PNV60-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "16. Rule 1: Stop the Action!"
      },
      {
        "type": "text",
        "text": "text/part0028_split_000.html#QMFO0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "17. Rule 2: See the Past … and Then the Future"
      },
      {
        "type": "text",
        "text": "text/part0029_split_000.html#RL0A0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "18. Rule 3: Say the Past … and Then the Future"
      },
      {
        "type": "text",
        "text": "text/part0030_split_000.html#SJGS0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "19. Rule 4: Externalize Key Information"
      },
      {
        "type": "text",
        "text": "text/part0031_split_000.html#TI1E0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "20. Rule 5: Feel the Future"
      },
      {
        "type": "text",
        "text": "text/part0032_split_000.html#UGI00-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "21. Rule 6: Break It Down … and Make It Matter"
      },
      {
        "type": "text",
        "text": "text/part0033_split_000.html#VF2I0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "22. Rule 7: Make Problems External, Physical, and Manual"
      },
      {
        "type": "text",
        "text": "text/part0034_split_000.html#10DJ40-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "23. Rule 8: Have a Sense of Humor!"
      },
      {
        "type": "text",
        "text": "text/part0035_split_000.html#11C3M0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "Step Five: Change Your Situation: Mastering ADHD in Specific Areas of Your Life"
      },
      {
        "type": "text",
        "text": "text/part0036_split_000.html#12AK80-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "24. Education"
      },
      {
        "type": "text",
        "text": "text/part0037_split_000.html#1394Q0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "25. Work"
      },
      {
        "type": "text",
        "text": "text/part0038_split_000.html#147LC0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "26. Money"
      },
      {
        "type": "text",
        "text": "text/part0039_split_000.html#1565U0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "27. Relationships"
      },
      {
        "type": "text",
        "text": "text/part0040_split_000.html#164MG0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "28. Driving, Health, and Lifestyle Risks"
      },
      {
        "type": "text",
        "text": "text/part0041_split_000.html#173720-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "29. Other Mental and Emotional Problems"
      },
      {
        "type": "text",
        "text": "text/part0042_split_000.html#181NK0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "30. Drugs and Crime"
      },
      {
        "type": "text",
        "text": "text/part0043_split_000.html#190860-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "Appendix: A Closer Look at ADHD Symptoms"
      },
      {
        "type": "text",
        "text": "text/part0044_split_000.html#19UOO0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "Resources"
      },
      {
        "type": "text",
        "text": "text/part0045.html#1AT9A0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "Index"
      },
      {
        "type": "text",
        "text": "text/part0046_split_000.html#1BRPS0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "About the Authors"
      },
      {
        "type": "text",
        "text": "text/part0047.html#1CQAE0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "About Guilford Press"
      },
      {
        "type": "text",
        "text": "text/part0048.html#1DOR00-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "Discover Related Guilford Books"
      },
      {
        "type": "text",
        "text": "text/part0049.html#1ENBI0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "Keep reading for a FREE excerpt from Taking Charge of ADHD: The Complete, Authoritative Guide for Parents, Fourth Edition"
      },
      {
        "type": "text",
        "text": "text/part0050_split_000.html#1FLS40-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "1. What Is Attention-Deficit/Hyperactivity Disorder?"
      },
      {
        "type": "text",
        "text": "text/part0051.html#1GKCM0-ccc77842d77249eb8d63b72d3693c8e9"
      },
      {
        "type": "text",
        "text": "Credit"
      },
      {
        "type": "text",
        "text": "text/part0052.html#1HIT80-ccc77842d77249eb8d63b72d3693c8e9"
      }
    ]
  }
]

---

### User
> 12/1/2025, 1:48:21 PM

[
  {
    "tool_use_id": "toolu_01MvBcUWsDk3r5zf2mtThNkz",
    "type": "tool_result",
    "content": [
      {
        "type": "text",
        "text": "Cover"
      },
      {
        "type": "text",
        "text": "xhtml/Pric_9780593235249_epub3_cvi_r1.xhtml"
      },
      {
        "type": "text",
        "text": "Title Page"
      },
      {
        "type": "text",
        "text": "xhtml/Pric_9780593235249_epub3_tp_r1.xhtml"
      },
      {
        "type": "text",
        "text": "Copyright"
      },
      {
        "type": "text",
        "text": "xhtml/Pric_9780593235249_epub3_cop_r1.xhtml"
      },
      {
        "type": "text",
        "text": "Contents"
      },
      {
        "type": "text",
        "text": "xhtml/Pric_9780593235249_epub3_toc_r1.xhtml"
      },
      {
        "type": "text",
        "text": "Introduction: Alienation"
      },
      {
        "type": "text",
        "text": "xhtml/Pric_9780593235249_epub3_itr_r1.xhtml"
      },
      {
        "type": "text",
        "text": "Chapter 1: What Is Autism, Really?"
      },
      {
        "type": "text",
        "text": "xhtml/Pric_9780593235249_epub3_c001_r1.xhtml"
      },
      {
        "type": "text",
        "text": "Chapter 2: Who Are the Masked Autistics?"
      },
      {
        "type": "text",
        "text": "xhtml/Pric_9780593235249_epub3_c002_r1.xhtml"
      },
      {
        "type": "text",
        "text": "Chapter 3: The Anatomy of the Mask"
      },
      {
        "type": "text",
        "text": "xhtml/Pric_9780593235249_epub3_c003_r1.xhtml"
      },
      {
        "type": "text",
        "text": "Chapter 4: The Cost of Masking"
      },
      {
        "type": "text",
        "text": "xhtml/Pric_9780593235249_epub3_c004_r1.xhtml"
      },
      {
        "type": "text",
        "text": "Chapter 5: Rethinking Autism"
      },
      {
        "type": "text",
        "text": "xhtml/Pric_9780593235249_epub3_c005_r1.xhtml"
      },
      {
        "type": "text",
        "text": "Chapter 6: Building an Autistic Life"
      },
      {
        "type": "text",
        "text": "xhtml/Pric_9780593235249_epub3_c006_r1.xhtml"
      },
      {
        "type": "text",
        "text": "Chapter 7: Cultivating Autistic Relationships"
      },
      {
        "type": "text",
        "text": "xhtml/Pric_9780593235249_epub3_c007_r1.xhtml"
      },
      {
        "type": "text",
        "text": "Chapter 8: Creating a Neurodiverse World"
      },
      {
        "type": "text",
        "text": "xhtml/Pric_9780593235249_epub3_c008_r1.xhtml"
      },
      {
        "type": "text",
        "text": "Conclusion: Integration"
      },
      {
        "type": "text",
        "text": "xhtml/Pric_9780593235249_epub3_c009_r1.xhtml"
      },
      {
        "type": "text",
        "text": "Dedication"
      },
      {
        "type": "text",
        "text": "xhtml/Pric_9780593235249_epub3_ded_r1.xhtml"
      },
      {
        "type": "text",
        "text": "Acknowledgments"
      },
      {
        "type": "text",
        "text": "xhtml/Pric_9780593235249_epub3_ack_r1.xhtml"
      },
      {
        "type": "text",
        "text": "Notes"
      },
      {
        "type": "text",
        "text": "xhtml/Pric_9780593235249_epub3_nts_r1.xhtml"
      },
      {
        "type": "text",
        "text": "Index"
      },
      {
        "type": "text",
        "text": "xhtml/Pric_9780593235249_epub3_idx_r1.xhtml"
      }
    ]
  }
]

---

### Assistant
> 12/1/2025, 1:48:28 PM

[
  {
    "type": "tool_use",
    "id": "toolu_01Q3r4FnVB44JYUqjdiZzuVZ",
    "name": "TodoWrite",
    "input": {
      "todos": [
        {
          "content": "Locate Barkley and Price ebooks in filesystem",
          "status": "completed",
          "activeForm": "Locating Barkley and Price ebooks in filesystem"
        },
        {
          "content": "Extract table of contents from both books",
          "status": "completed",
          "activeForm": "Extracting table of contents from both books"
        },
        {
          "content": "Read relevant chapters on ADHD dimensions and assessment",
          "status": "in_progress",
          "activeForm": "Reading relevant chapters on ADHD dimensions and assessment"
        },
        {
          "content": "Read relevant chapters on individual variation and profiles",
          "status": "pending",
          "activeForm": "Reading relevant chapters on individual variation and profiles"
        },
        {
          "content": "Synthesize findings into structured profile dimensions",
          "status": "pending",
          "activeForm": "Synthesizing findings into structured profile dimensions"
        }
      ]
    }
  }
]

---

### User
> 12/1/2025, 1:48:28 PM

[
  {
    "tool_use_id": "toolu_01Q3r4FnVB44JYUqjdiZzuVZ",
    "type": "tool_result",
    "content": "Todos have been modified successfully. Ensure that you continue to use the todo list to track your progress. Please proceed with the current tasks if applicable"
  }
]

---

### Assistant
> 12/1/2025, 1:48:35 PM

[
  {
    "type": "text",
    "text": "Now let me read the key chapters. From the TOCs, I can see:\n\n**Barkley's book** - Chapters 6-10 cover the nature of ADHD, executive functions, and self-control\n**Price's book** - Chapters 1-3 cover what autism is, who masked autistics are, and the anatomy of masking"
  }
]

---

### Assistant
> 12/1/2025, 1:48:36 PM

[
  {
    "type": "tool_use",
    "id": "toolu_01HBSt63TfPc1cjyNXoGzyyE",
    "name": "mcp__ebook-mcp__get_epub_chapter_markdown",
    "input": {
      "epub_path": "/home/chris/dev/projects/codex/brain_explore/books/Taking Charge of Adult ADHD Second Edition.epub",
      "chapter_id": "text/part0016_split_000.html"
    }
  }
]

---

### Assistant
> 12/1/2025, 1:48:37 PM

[
  {
    "type": "tool_use",
    "id": "toolu_017tcUncY4PWJTvYMsQAGpX2",
    "name": "mcp__ebook-mcp__get_epub_chapter_markdown",
    "input": {
      "epub_path": "/home/chris/dev/projects/codex/brain_explore/books/Taking Charge of Adult ADHD Second Edition.epub",
      "chapter_id": "text/part0019_split_000.html"
    }
  }
]

---

### Assistant
> 12/1/2025, 1:48:38 PM

[
  {
    "type": "tool_use",
    "id": "toolu_01BaJMeDeRzQ8Wx3bbM8X3cS",
    "name": "mcp__ebook-mcp__get_epub_chapter_markdown",
    "input": {
      "epub_path": "/home/chris/dev/projects/codex/brain_explore/books/Taking Charge of Adult ADHD Second Edition.epub",
      "chapter_id": "text/part0020_split_000.html"
    }
  }
]

---

### User
> 12/1/2025, 1:48:38 PM

[
  {
    "type": "tool_result",
    "content": "Error executing tool get_epub_chapter_markdown: text/part0016_split_000.html not found in TOC.",
    "is_error": true,
    "tool_use_id": "toolu_01HBSt63TfPc1cjyNXoGzyyE"
  }
]

---

### User
> 12/1/2025, 1:48:38 PM

[
  {
    "type": "tool_result",
    "content": "Error executing tool get_epub_chapter_markdown: text/part0019_split_000.html not found in TOC.",
    "is_error": true,
    "tool_use_id": "toolu_017tcUncY4PWJTvYMsQAGpX2"
  }
]

---

### User
> 12/1/2025, 1:48:38 PM

[
  {
    "type": "tool_result",
    "content": "Error executing tool get_epub_chapter_markdown: text/part0020_split_000.html not found in TOC.",
    "is_error": true,
    "tool_use_id": "toolu_01BaJMeDeRzQ8Wx3bbM8X3cS"
  }
]

---

### Assistant
> 12/1/2025, 1:48:44 PM

[
  {
    "type": "text",
    "text": "Let me try without the split suffix:"
  }
]

---

### Assistant
> 12/1/2025, 1:48:44 PM

[
  {
    "type": "tool_use",
    "id": "toolu_01GicbMMHMjV7TtS1Nr6cC9X",
    "name": "mcp__ebook-mcp__get_epub_chapter_markdown",
    "input": {
      "epub_path": "/home/chris/dev/projects/codex/brain_explore/books/Taking Charge of Adult ADHD Second Edition.epub",
      "chapter_id": "text/part0016.html"
    }
  }
]

---

### Assistant
> 12/1/2025, 1:48:45 PM

[
  {
    "type": "tool_use",
    "id": "toolu_01PrFwMUMYpZqrvhtGPu7Yqa",
    "name": "mcp__ebook-mcp__get_epub_chapter_markdown",
    "input": {
      "epub_path": "/home/chris/dev/projects/codex/brain_explore/books/Taking Charge of Adult ADHD Second Edition.epub",
      "chapter_id": "text/part0019.html"
    }
  }
]

---

### User
> 12/1/2025, 1:48:45 PM

[
  {
    "type": "tool_result",
    "content": "Error executing tool get_epub_chapter_markdown: text/part0016.html not found in TOC.",
    "is_error": true,
    "tool_use_id": "toolu_01GicbMMHMjV7TtS1Nr6cC9X"
  }
]

---

### User
> 12/1/2025, 1:48:45 PM

[
  {
    "type": "tool_result",
    "content": "Error executing tool get_epub_chapter_markdown: text/part0019.html not found in TOC.",
    "is_error": true,
    "tool_use_id": "toolu_01PrFwMUMYpZqrvhtGPu7Yqa"
  }
]

---

### Assistant
> 12/1/2025, 1:48:49 PM

[
  {
    "type": "text",
    "text": "Let me check the actual TOC format more carefully and use the exact links:"
  }
]

---

### Assistant
> 12/1/2025, 1:48:51 PM

[
  {
    "type": "tool_use",
    "id": "toolu_01ADTGkd13kdqfbiotiC9FNH",
    "name": "mcp__ebook-mcp__get_epub_chapter_markdown",
    "input": {
      "epub_path": "/home/chris/dev/projects/codex/brain_explore/books/Taking Charge of Adult ADHD Second Edition.epub",
      "chapter_id": "text/part0010_split_000.html#9H5K0-ccc77842d77249eb8d63b72d3693c8e9"
    }
  }
]

---

### User
> 12/1/2025, 1:48:51 PM

[
  {
    "type": "tool_result",
    "content": "Error executing tool get_epub_chapter_markdown: Anchor 9H5K0-ccc77842d77249eb8d63b72d3693c8e9 not found in text/part0010_split_000.html",
    "is_error": true,
    "tool_use_id": "toolu_01ADTGkd13kdqfbiotiC9FNH"
  }
]

---

### Assistant
> 12/1/2025, 1:48:57 PM

[
  {
    "type": "tool_use",
    "id": "toolu_01UkjZEjnt3pCh6Et4ALUNGk",
    "name": "mcp__ebook-mcp__get_epub_chapter_markdown",
    "input": {
      "epub_path": "/home/chris/dev/projects/codex/brain_explore/books/Taking Charge of Adult ADHD Second Edition.epub",
      "chapter_id": "text/part0010_split_000.html"
    }
  }
]

---

### Assistant
> 12/1/2025, 1:48:58 PM

[
  {
    "type": "tool_use",
    "id": "toolu_0186RSygDrZuBXPiSpPbDABQ",
    "name": "mcp__ebook-mcp__get_epub_chapter_markdown",
    "input": {
      "epub_path": "/home/chris/dev/projects/codex/brain_explore/books/Unmasking Autism.epub",
      "chapter_id": "xhtml/Pric_9780593235249_epub3_c001_r1.xhtml"
    }
  }
]

---

### User
> 12/1/2025, 1:48:58 PM

[
  {
    "type": "tool_result",
    "content": "Error executing tool get_epub_chapter_markdown: text/part0010_split_000.html not found in TOC.",
    "is_error": true,
    "tool_use_id": "toolu_01UkjZEjnt3pCh6Et4ALUNGk"
  }
]

---

### User
> 12/1/2025, 1:49:00 PM

[
  {
    "tool_use_id": "toolu_0186RSygDrZuBXPiSpPbDABQ",
    "type": "tool_result",
    "content": [
      {
        "type": "text",
        "text": "# CHAPTER 1\n\n# What Is Autism, Really?\n\nWhen Crystal was young, she exhibited many behaviors psychologists today would\nrecognize as traditionally Autistic: she lined up toys in rows instead of\nplaying pretend with them, chewed on her blanket while staring at the wall,\nand had trouble understanding in-jokes and teasing. But she didn’t “look\nAutistic enough” to get easily diagnosed in the 1990s, when she was growing\nup.\n\n“My mom actually thought I should get assessed,” she says. “But my grandpa\nshut it down. He was all, no, no way, Crystal’s such a good girl! There’s\nnothing wrong with her. Don’t even think about stuff like that.”\n\nCrystal’s grandfather probably figured he was protecting her from getting\nstuck with a label that would bring a lifetime of abuse. He certainly isn’t\nalone in that. Label avoidance (taking steps to evade diagnosis) is a very\ncommon consequence of disability and mental health\nstigma.[[1]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7494 \"note\") Publicly\nidentifying as disabled does mean being viewed as less competent—and less\nhuman—by many people. As damaging and self-defeating as it can be to\ncamouflage one’s disability status, it is by no means a paranoid act. It’s a\nrational reflection of the prejudices disabled people face. It’s not unique to\nAutism, either; many people with mental\nillnesses[[2]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7508 \"note\") and\nhidden physical\ndisabilities[[3]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7519 \"note\")\nelect to avoid the mark of shame a diagnosis might bring.\n\nMy dad hid his cerebral palsy and seizure disorder for his entire life. No one\nknew about his condition other than my grandmother, my mom, and eventually me.\nHe never went to college because he would have needed to reveal his access\nneeds to campus disability services. He only ever applied to jobs that didn’t\nrequire him to write or type, lest his poor fine motor control be revealed. As\na child, I typed up the flyers for his lawn mowing business, because he\ncouldn’t work the computer himself. I only found out about his condition as a\nteenager; he sobbingly confessed it to me, as if it were a terrible secret,\nafter his marriage to my mother had already fallen apart. He told me that his\nmother had made him hide his condition because it wouldn’t have been\nacceptable to be openly disabled in the tiny Appalachian town where he grew\nup. Shame and self-loathing followed him until the day that he died of\ndiabetes (a condition he developed as an adult and also refused to treat).\n\nI didn’t find out I was Autistic until many years after his death, but he was\nthe first person who demonstrated to me just how painful and self-destructive\nhiding your disability can be. He had erected an entire life around hiding who\nhe was, and his defensive mechanisms had slowly killed him.\n\nLabel avoidance was common among the parents of potentially Autistic children\nduring the 1990s, because the condition was so poorly understood and\ndemonized.[[4]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7530 \"note\")\nAutistic people were assumed to be intellectually disabled, and intellectually\ndisabled people were not valued or respected, so many families did their\ndamnedest to keep the label off their kids’ backs. Though Crystal’s\ngrandfather intended to protect her from bigotry, and from being infantilized,\nhe also denied her important self-knowledge, educational resources, and a\nplace in the Autistic community. Without consulting Crystal, her family\ndetermined it would be better for her to suffer and hide her neurodiversity\nthan to have a name for her marginalized position in the world. The weight of\nthis decision is one Crystal continues to deal with now, as an adult who was\ndiagnosed in her late twenties.\n\n“Now I know I’m Autistic, but I kinda found out about it too late,” she says.\n“If I tell people, they don’t want to believe me. I have my life together too\nmuch for them to realize how hard it all is. Nobody wants to hear now about\nhow hard it’s always been, always still is, frankly.”\n\nAt this point, I have heard hundreds of Autistic people tell versions of\nCrystal’s story. Some of the details change, but the narrative arc is always\nthe same: A child exhibits early signs of difficulty, but their families and\nteachers balk when disability is raised. Parents or grandparents who\nthemselves have Autism spectrum traits dismiss the child’s complaints,\nclaiming that everybody suffers from the social stress, sensory sensitivities,\nstomach issues, or cognitive fuzziness they themselves experience. Everyone in\nthe child’s life views disability not as an explanation of how a person\nfunctions (and what help they need in order to function), but a sign of\ndamage. So they push the label away, and tell their child to stop making such\na fuss. Believing they are helping their child “rise above” a limitation and\nbe tough, they encourage the child not to be visibly odd, or to ever ask for\nassistance.\n\nThough a masked Autistic child has no way of explaining why they find life so\ndifficult, they suffer all the same. Peers detect there’s something unnameably\n“off” about them, and exclude them despite their best attempts at\nfriendliness. When the child makes themselves small and inobtrusive, they’re\ngranted some of the affection they desperately crave and never get enough of.\nSo they do it more and more, quieting the voice inside themselves that says\nhow they’re being treated isn’t fair. They work hard, demand little, and play\nby society’s rules as closely as possible. They grow into an adult who is even\nmore self-effacing, and even less capable of voicing how they feel. Then,\nafter decades of forcing themselves into a restrictive neurotypical box, they\nhave some kind of breakdown that finally makes all the turmoil bubbling\nbeneath the surface impossible to ignore. It’s only then that they discover\nthey’re Autistic.\n\nIn Crystal’s case, the breaking point took the form of a months-long case of\nAutistic burnout. Autistic burnout is a state of chronic exhaustion where an\nAutistic person’s skills begin to degrade, and their tolerance to stress is\ngreatly reduced.[[5]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7541 \"note\")\nIt hit Crystal like a Mack truck after she completed her senior thesis in\ncollege. College had taken her a few years longer than the rest of her\nfriends, though she couldn’t explain exactly why. She was always having to\ndrop classes in order to hold her life together. A full course load just\nwasn’t possible. When people asked about it, she lied and said she also worked\na full-time job.\n\nIn her final year of college, Crystal was required to oversee set design for\nthe theater department’s biggest show of the year. Designing dozens of props,\nsourcing their materials, managing the building of them, and then keeping\ntrack of all the items in a big Google spreadsheet was simply too stressful\nfor her to manage, especially while taking her final remaining classes. She\npushed through, losing hair and losing weight, but once the project was\ncompleted, she collapsed.\n\n“After I graduated, I was in bed at my mom’s house for three months,” she\nsays. “Didn’t apply to jobs. I barely showered, had all these McDonald’s\nwrappers on the floor of my bedroom, and my family still insisted I was just\nbeing lazy.”\n\nEventually, Crystal became so lethargic that she no longer wanted to watch TV\nor play with the family dog. That was concerning enough for her mother to\nsuggest she go see a therapist. An Autism assessment came shortly thereafter.\n\n“At first I couldn’t believe it,” Crystal says. “My family still doesn’t\nbelieve it. They had every indication, my whole life, but they don’t want to\nsee it.”\n\nAt last, Crystal had an explanation for why she couldn’t get as much done as\nother people, and why basic-seeming tasks like running to the bank or sitting\nthrough a two-hour lecture left her too tired to think or speak. Regular life\nactually did require more willpower out of her; Autistic people frequently\nexperience inertia in starting a\ntask,[[6]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7552 \"note\") and\nchallenges in breaking complex activities down into small steps that follow a\nlogical sequence.[[7]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7557\n\"note\") This can make everything from basic household chores to applying to\njobs and filing taxes incredibly challenging, or even impossible without help.\n\nIn addition to all the baseline cognitive and sensory challenges that came\nwith Autism for Crystal, she was also having to put a lot of energy into\nalways seeming “normal.” She constantly fought the urge to suck on her\nfingers, and when people spoke to her, she had to forcibly point her attention\nat their words and face. Reading a book took her twice as long as the average\nperson. All she had the energy to do at the end of the day was sit in bed and\neat french fries. Crystal’s mother and grandfather were unsatisfied by this\nnewfound explanation, though. They said that if she had really been hurting\nthat bad all her life, they would have realized it.\n\n“I wish I could make them understand,” she says, “Autism isn’t what you\nthink.”\n\n# Defining Autism\n\nOne of the reasons Autism often gets overlooked in women like Crystal is a\nfundamental misunderstanding that professionals and the public have about what\nAutism even is. Until fairly recently, most people believed Autism was rare,\nthat only young boys had it, and that it was always easy to see. Think of\nDustin Hoffman’s portrayal in the film _Rain Man_ : he’s institutionalized as\na child because he’s profoundly disabled and too “difficult” to have at home,\nhe never gives eye contact, wanders off dangerously when not closely watched,\nand has a preternatural talent for math that his nondisabled brother exploits\nfor personal gain. This is how all of us were trained to view the disability:\na horrible condition that renders you freakish and helpless, your life only as\nvaluable as your savant-like skills are to other people.\n\nBy the mid-1990s, when Crystal was a kid, some people also had a vague\nawareness of what was then called Asperger’s Disorder. Asperger’s was\nstereotyped as a “higher functioning” flavor of Autism found in really smart,\nnerdy, usually rude men who worked in fields like tech. In both forms, Autism\nwas associated with being awkward and uncaring (and male) with a penchant for\nnumbers. People had little to no understanding of Autism’s causes, what it\nfelt like to be an Autistic person, or that the disability shares features\nwith other disorders like epilepsy, Social Anxiety Disorder, Attention-Deficit\nHyperactive Disorder (ADHD), or Post-Traumatic Stress Disorder (PTSD).\n\nDespite what people believe, Autism is not defined by rudeness, masculinity,\nor having any kind of mathematical skill. In the scientific literature, it’s\narguable whether the disability should even be defined by the presence of\nclear behavioral signs, such as trouble reading social cues or hesitating to\ninitiate contact with other\npeople.[[8]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7568 \"note\") Instead\nof looking to the external signals of Autism that others might pick up on,\nit’s important that we instead focus on the neurobiological markers of the\nneurotype, and the internal experiences and challenges that Autistic people\nthemselves report.\n\n**_Autism is neurological._** Autism is a developmental disability that runs\nin families[[9]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7576 \"note\") and\nappears to be largely genetically\nheritable.[[10]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7584 \"note\")\nHowever, it is also _multiply determined,_ meaning it has no single cause: a\nwhole host of different genes appear to be associated with\nAutism,[[11]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7595 \"note\") and\nevery Autistic person’s brain is unique and exhibits its own distinct patterns\nof connectivity.[[12]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7607\n\"note\") Autism is a _developmental_ disability because compared to\nneurotypical milestones, it comes with delays: many Autistic people continue\nto grow in their social and emotional skills for much later in life than\nallistics tend to.[[13]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7621\n\"note\") (However, this may be due to the fact that Autistic people are forced\nto develop our own social and emotional coping skills from scratch, because\nthe neurotypical methods taught to us don’t suit how we process\ninformation—more on this later.) Autism is associated with specific and\npervasive differences in the brain, which result in us diverging from\nneurotypical standards, in terms of how our brains filter and make sense of\ninformation.\n\nAutistic people have differences in the development of their anterior\ncingulate cortex,[[14]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7632\n\"note\") a part of the brain that helps regulate attention, decision making,\nimpulse control, and emotional processing. Throughout our brains, Autistic\npeople have delayed and reduced development of Von Economo neurons (or VENs),\nbrain cells that help with rapid, intuitive processing of complex\nsituations.[[15]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7646 \"note\")\nSimilarly, Autistic brains differ from allistic brains in how excitable our\nneurons are.[[16]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7659 \"note\") To\nput it in very simple terms, our neurons activate easily, and don’t\ndiscriminate as readily between a “nuisance variable” that our brains might\nwish to ignore (for example, a dripping faucet in another room) and a crucial\npiece of data that deserves a ton of our attention (for example, a loved one\nbeginning to quietly cry in the other room). This means we can both be easily\ndistracted by a small stimulus and miss a large meaningful one.\n\nAutistic brains have unique connection patterns that deviate from what is\nnormally observed in neurotypical people. When infants are born, their brains\nare typically hyperconnected; much of human development is a process of slowly\npruning unhelpful connections and becoming more efficient at responding to\none’s environment, based on life experience and learning. In Autistic brains,\nhowever, researchers have found that some regions remain hyperconnected\nthroughout the life span, whereas other regions may be underconnected\n(relatively speaking). It is difficult to sum up these connectivity patterns\nbecause, as neurobiologists at the Weizmann Institute of Science have found,\nevery Autistic brain exhibits a different connectivity pattern. Our brain\nwiring appears to actually be more diverse than the wiring of neurotypical\nbrains, which researchers believe have a consistent pruning\npattern.[[17]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7670 \"note\") The\nresearchers at the Weizmann Institute have theorized that this means Autistic\nbrains respond to our environments differently; whereas neurotypical brains\nare believed to readily adapt to the sensory and social input they receive\nfrom the outside world, Autistic brain development and pruning appears to be\n“disrupted.”[[18]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7687 \"note\")\n\nAutistic people also exhibit less of what neuroscientists call _global-to-\nlocal interference_ :[[19]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7695\n\"note\") we are inclined to zero in on small details, even when those details\ndon’t jibe with the overall “big picture” that a non-Autistic person might\nsee. For example, one series of studies found that Autistic people are far\nbetter than allistics at copying down a drawing of a distorted 3-D object that\ncouldn’t exist in real\nlife.[[20]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7709 \"note\") Allistics\ngot caught off guard by how impossible and illogical the overall image was,\nwhereas Autistics could just focus on the individual lines and shapes that\nmade up the image, and re-create the drawing from the bottom up. This high\ndegree of attention to detail also applies to how we navigate social\nsituations: we focus on the small features of a person’s face rather than\ntaking in their likeness or emotional expression as a whole, for\ninstance.[[21]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7717 \"note\") This\nhelps explain why many Autistic people have _prosopagnosia_ (the inability to\nrecognize faces),[[22]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7725\n\"note\") and experience difficulty reading emotions on neurotypicals’ faces.\n\nTogether, all of this means that Autistic people tend to have the following\nqualities:\n\n  * We are hyperreactive to even small stimuli in our environment\n\n  * We have trouble distinguishing between information or sensory data that should be ignored versus data that should be carefully considered\n\n  * We are highly focused on details rather than “big picture” concepts\n\n  * We’re deeply and deliberatively analytical\n\n  * Our decision-making process is methodical rather than efficient; we don’t rely on mental shortcuts or “gut feelings”\n\n  * Processing a situation takes us more time and energy than it does for a neurotypical person\n\nNow that I’ve explained some of the neurological markers correlated with\nAutism, I think it’s important to clarify a finer point: the fact that a\ndisability has some biological markers does not mean it is more “real” or\nlegitimate than a disability that you can only observe in a person’s behavior.\nAnd Autism is still diagnosed based on behavior and reported challenges the\nAutistic person is facing, not on a brain scan. The fact that Autism has\nneurological features doesn’t mean it is a more sympathetic disability than,\nsay, an eating disorder or substance addiction. It also doesn’t mean Autistics\nare doomed to always function in a particular way, or to always struggle.\n\nWhile understanding the biology of human difference is helpful in a lot of\nways, there are real risks to reducing a disability to its physical “causes.”\nIt can lead people to believe that our biology is our destiny, and that we are\nlesser to neurotypicals in some unchangeable way. In fact, some research\nsuggests that when people understand disabilities such as depression and ADHD\nas being purely biological, they actually show more stigma toward people with\nthose conditions, not\nless.[[23]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7737 \"note\") The idea\nthat a disabled group _can’t help being the way they are_ is dehumanizing and\nrestrictive, even though some also find it liberating and validating.\n\nWhen society first starts flirting with accepting a marginalized group, that\nacceptance is often wrapped up in a _born this way_ type narrative. For\nexample, in the early 2000s, many straight allies claimed to support gay\npeople because being gay wasn’t a choice, and we couldn’t help being the way\nthat we are. There was a lot of pop science writing at that time exploring the\nsearch for the “gay\ngene,”[[24]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7748 \"note\") and\nsuggesting that certain hormone exposures in the womb might predispose a fetus\nto being gay. Today we don’t have conversations about the biological causes of\ngayness very much anymore. In the United States at least, being gay has\nstarted becoming accepted enough that queer people don’t have to justify our\nexistence by saying we can’t help but be this way. If someone were to choose\nto be gay, that wouldn’t be a problem, because being gay is good. Similarly,\nAutistic people deserve acceptance, not because we can’t help but have the\nbrains we have, but because being Autistic is good.\n\n**_Autism is associated with a deliberative processing style._** When making\nsense of the world, Autistic people usually defer to logic and reason rather\nthan emotion or intuition. We dive deep into all the pros and cons, sometimes\nexcessively so, not knowing where to draw the line between an important\nvariable and an unimportant one. We tend not to get habituated to familiar\nsituations or stimuli as readily as other people, so we often think through a\nsituation as if it’s completely new to us, even if it\nisn’t.[[25]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7756 \"note\") All of\nthis requires a lot of energy, focus, and time, so we get exhausted and\noverloaded quite easily. However, it also makes us less prone to errors.\nExperimental research shows that Autistic people are far less susceptible to\nthe biases allistic people commonly fall prey\nto.[[26]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7764 \"note\") For\nexample, consider this relatively simple problem:\n\n> _A bat and a ball together cost $1.10. The bat costs $1.00 more than the\n> ball. How much does the ball cost?_\n\nIn experimental studies, over 80 percent of non-Autistic people get this\nquestion wrong. They parse the question quickly, go with their gut, and answer\nthat the ball must cost ten\ncents.[[27]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7775 \"note\") The\ncorrect answer is that the ball costs five cents, and the bat costs a dollar\nmore, $1.05, which together adds up to $1.10. It takes an extra moment of\ncareful processing to skip the “obvious” (and wrong) answer and provide the\ncorrect one. For most allistic people, the default way of thinking is to go\nwith what’s obvious. But since Autistic people do not process information\nintuitively, we don’t see “obvious” answers to things, and have to carefully\nbreak the question down instead. This results in us being far more likely to\nget the answer right.\n\nThis slow, deliberative style of processing comes with its fair share of\ndownsides. We can’t always pick up on irony or “obvious” implied meanings\npeople haven’t said explicitly. Allistic people often accuse us of\noverthinking things, or being too slow and hesitant to come up with a\nresponse. We also get overwhelmed when presented with mountains of data, which\nneurotypical people find much easier to just ignore.\n\n**_Autistic people process the world from the bottom up_**. If you want to\nunderstand Autism as a disability and a source of human difference at a\nglance, it’s best summed up this way: we process in a careful, systematic,\nbottom-up way. Allistic folks, in contrast, make sense of the world in a very\ntop-down fashion. They’ll enter a new environment, such as an unfamiliar\nrestaurant, take a quick look around, and jump to reasonable conclusions about\nhow to order, where to sit, what kind of service to expect, and even how\nloudly they should talk. Their brains will immediately begin to filter through\nsounds, lights, and other stimuli, and adjust accordingly. They might notice a\nclanging pinball machine in the corner for a moment, for instance, but soon\nhabituate to it, and become able to ignore it. When the waiter approaches,\nthey probably can chat without much difficulty, even if something unexpected\ngets said or the item they planned to order is sold out. They don’t rely on\nmemorized conversational scripts, and they don’t have to carefully parse every\nsingle piece of data they encounter to make sense of it. They can wing it.\n\nAutistic people, on the flip side, don’t rely on knee-jerk assumptions or\nquick mental shortcuts to make our decisions. We process each element of our\nenvironment separately, and intentionally, taking very little for granted. If\nwe’ve never been in a particular restaurant before, we may be slow to make\nsense of its layout or figure out how ordering works. We’ll need really clear-\ncut indications of whether it’s the kind of place where you sit down and get\ntable service, or if you’re supposed to go to a counter to ask for what you\nlike. (Many of us try to camouflage this fact by doing extensive research on a\nrestaurant before setting foot inside.) Every single light, laugh, and smell\nin the place is taken in individually by our sensory system, rather than\nblended into a cohesive whole. To cope with unpredictability, we analyze our\nexperiences for patterns, and memorize rule sets: _if the waiter says X, I\nreply with Y_. When something unexpected happens, we have to carefully sort\nout how to respond. Too much change may cause us to become really exhausted,\nor to freak out.\n\n**_Autism touches every part of the Autistic person’s life._** Of course, many\nnon-Autistic people might resonate with some of the feelings and sensations I\njust described. There’s a difference between being _allistic_ (which simply\nmeans non-Autistic) and being fully _neurotypical_ (which means lacking any\nmental illness or cognitive disability). An allistic person with a social\nanxiety disorder may also feel overwhelmed in busy bars and restaurants, just\nas Autistic people do. Someone with post-traumatic stress disorder may\nsimilarly be rattled by a noisy pinball machine. The difference between Autism\nand these other disorders, however, is that Autism is a cognitive and sensory\ndifference that affects every area of life. You wouldn’t expect a socially\nanxious person to get overwhelmed by the sound of a clanking radiator when\nthey’re alone at home, for example (unless they’re also Autistic or have a\nsensory processing disorder).\n\nBecause the neural and cognitive features of Autism are so pervasive, it\naffects almost every aspect of a person’s body and brain. It’s related to\ncoordination and muscle tone, the ability to read emotions on people’s faces,\ncommunication skills, reaction time, and even how a person recognizes feelings\nof pain or hunger.[[28]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7786\n\"note\") When I look at a person’s face, I don’t simply see “happiness” or\n“sadness” radiating off them, for example; I see minute changes in their eyes,\nforehead, mouth, breathing, and posture, which I then have to effortfully\npiece together to make an informed guess about how they feel. Often, it’s too\nmuch discordant data to make sense of. When I don’t have the energy to\ncarefully process others’ emotional expressions, people are inscrutable to me\nand arouse a lot of anxiety.\n\nAutism can influence how intensely we focus on an activity, and how we\nperceive textures, tastes, and\nsounds.[[29]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7797 \"note\") Autism\ncan predispose a person to having fanatical interests (often referred to as\n_special interests_)[[30]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7808\n\"note\") and to following rules very rigidly. Many of us have trouble\nidentifying sarcasm or reading nonverbal signals. Disruptions to our routines\nor expectations can make us panic. Learning new skills may take us far longer\nthan other people.\n\n**_Autism is behavioral._** Autism is associated with repetitive self-\nstimulatory behavior\n(“stimming”),[[31]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7820 \"note\")\nwhich can be something as benign as hand-flapping, or as severe as chewing\none’s fingers until they bleed. Stimming is an important means of self-\nregulation. It helps soothe us when we’re anxious or overloaded with stress,\nand it helps us express joy and enthusiasm. There are a variety of ways to\nstim, and stimming can make use of any of the five senses. Some of us stim\nusing _echolalia_ , the repeating of words, sounds, or phrases that feel good\nvibrating in our throats. Others stim by engaging the body’s _proprioceptive_\n_system_ (the neural system that tracks the body’s physical movement) by\njumping up and down or swaying in place. Sucking on candy, smelling scented\ncandles, staring at lava lamps, listening to recordings of rain and\nthunder—all of these activities can be stims. All humans stim to an extent (if\nthey didn’t, fidget spinners wouldn’t have become so popular several years\nago), but Autistic people stim more frequently, more repetitively, and more\nintensely than neurotypicals do.\n\nRepetitiveness is a key feature of Autistic behavior, according to the\n_Diagnostic and Statistical Manual of Mental Disorders_ (the _DSM_). And it is\ntrue that many of us crave the stability that repetition provides. Because we\nfind the external social world so unpredictable, most of us prefer consistent\nroutines. We often eat the same meals over and over again, or only enjoy a\nlimited range of foods (sometimes called _samefoods_ in the community). We\nhyperfixate on activities that we enjoy and can get so engrossed in them that\nwe forget to eat or take a break to stretch our legs. We echo phrases from\nmovies and TV because they help us emulate “normal” social behavior, or\nbecause we lack our own words for how we are feeling, or simply because the\nsounds feel pleasant to have vibrating in our vocal cords. Even having special\ninterests can be viewed as a repetitive behavior. Many of us watch the same\nmovies over and over or read and compile facts about our favorite subjects far\nbeyond the point that an allistic person would find entertaining.\n\nFor many masked Autistic people, however, repetitive behavior is something\nthat needs to remain hidden. If you chew your fingers a lot or keep humming\nthe same three-note tune to yourself, people will notice and mock you for it.\nIf you come across as _too_ obsessed with a weird subject (say, mortuary\nscience), people will be put off by your enthusiasm and keep their distance.\nMost of us have to figure out ways to conceal our stimming and special\ninterests. We might maintain a secret blog about our interests, for example,\nor find socially acceptable ways to get our energy out, such as long-distance\nrunning or fidgeting with our phones.\n\n**_Autistic people are at risk._** Timotheus Gordon Jr. is an Autistic\nresearcher, advocate, and the founder of Autistics Against Curing Autism\nChicago. He tells me that for him, choosing to stim (or how to stim) is highly\ndependent on which neighborhood he’s in, and how people are likely to react.\n\n“Walking into certain neighborhoods in Chicago or in the Chicagoland area, I\ncan’t wear my headphones to enjoy music,” he says, “otherwise I’ll get robbed\npotentially. Or if I walk around and fidget with toys, police or certain\npeople in the neighborhood will think I’m strange or doing something illegal\nand I might get arrested, killed, or beat up.”\n\nTimotheus says that in some circumstances, he masks his need to stim by\nchoosing a more socially acceptable outlet, such as bouncing a basketball. As\na Black Autistic person, he is frequently having to take the temperature of\nhis surroundings, gauging how others will react to his actions, and modulating\nhimself accordingly. The risks of being himself are simply too great to take\nfor granted.\n\nAutistic people are at a high risk of violence, as well as negative mental\nhealth outcomes. Since we can’t openly stim or engage in other repetitive\nbehaviors, some masked Autistic people reach for flawed coping strategies to\nhelp manage stress. We’re at an elevated risk of eating\ndisorders,[[32]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7831 \"note\")\nalcoholism and drug\naddiction,[[33]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7842 \"note\") and\ninsecure attachments to\nothers.[[34]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7854 \"note\") We tend\nto maintain shallow relationships, out of fear that people would hate getting\nto know our “real selves.” We may withdraw from other people, leading to\nnegative emotional and psychological outcomes. And the more isolated we are,\nthe less practice we get socializing, leading to a feedback loop of social\ndisempowerment and shame.\n\nAutism is also highly correlated with physical symptoms such as\ngastrointestinal\nissues,[[35]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7865 \"note\")\nconnective tissue\ndisorders,[[36]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7876 \"note\") and\nseizures[[37]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7887 \"note\")\nlargely for genetic reasons. It co-occurs with other disabilities such as\nAttention Deficit Hyperactive Disorder\n(ADHD)[[38]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7898 \"note\") and\ndyslexia at a high\nrate.[[39]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7909 \"note\") Many\nAutistic people have trauma histories and post-traumatic stress symptoms, and\nas I’ve already mentioned, a lifetime of masking puts us at a high risk of\nconditions like depression and\nanxiety.[[40]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7917 \"note\") These\nare some of the most common conditions that co-occur alongside Autism, but\nlater in the book we’ll discuss additional disorders that overlap (or are\nmistaken for) Autism.\n\n**_Autism is a neurodivergence._** Autism is a type of functioning (or a\n_neurotype_) that differs from what psychology defines as normative or\nneurotypical (NT). Autism is a particularly diverse and varied form of\nneurodivergence; there are just so many ways in which we are punished for\ndeviating from the norm. Every case of Autism is a bit different, and traits\ncan present in seemingly contradictory ways. Some Autistic people can’t speak;\nothers are incredibly hyperverbal from a young age, with huge vocabularies.\nSome Autistics can read people’s emotions so easily that it’s overwhelming;\nothers empathize with animals or objects, but not people; some of us have zero\nemotional empathy.[[41]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7928\n\"note\") But all of us are full-formed humans with a capacity to care for\nothers and behave ethically. Some Autistic people have no “special interests”;\nothers are fanatical about dozens of subjects. Some of us have skills we are\nadept at; others need help in every facet of our existence. What unites us,\ngenerally speaking, is a bottom-up processing style that impacts every aspect\nof our lives and how we move through the world, and the myriad practical and\nsocial challenges that come with being different.\n\nSince mainstream standards for behavior are so narrow, there are a variety of\nways in which a person can diverge—and be punished for diverging. Having\nfrequent panic attacks is a neurodivergence, as is exhibiting signs of an\neating disorder. If you struggle in your close relationships because of\nattachment trauma or an inescapable fear of rejection, you’re neurodivergent\ntoo (you might also get stuck with a particularly stigmatizing label, such as\nBorderline Personality Disorder).\n\nAlmost anyone can be viewed as defective or abnormal under our current\nmedicalized model of mental illness—at least during particularly trying\nperiods of their lives when they are depressed or their coping breaks down. In\nthis way, neurotypicality is more of an oppressive cultural standard than it\nactually is a privileged identity a person has. Essentially no one lives up to\nneurotypical standards all of the time, and the rigidity of those standards\nharms everyone.[[42]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7936 \"note\")\nMuch as heteronormativity harms straight and queer folks alike,\nneurotypicality hurts people no matter their mental health status.\n\nAutism is just one source of _neurodiversity_ in our world. The term\n_neurodiverse_ refers to the wide spectrum of individuals whose thoughts,\nemotions, or behaviors have been stigmatized as unhealthy, abnormal, or\ndangerous. The term was coined in 1999 by sociologist Judy Singer. In her\nhonor’s thesis, Singer wrote about the difficulty of making sense of her\ndaughter’s disabilities, which closely resembled traits her own mother\nexhibited when Singer was growing up. At the point that Singer was writing,\nAutism was poorly understood, and adults with Autistic traits, such as\nSinger’s mother (and Singer herself) rarely received diagnoses. Singer’s\ndaughter seemed to inhabit a space somewhere between Autism, ADHD, and a\nvariety of other disabilities. All three women were difficult to neatly\ncategorize, which only obscured just how marginalized and socially adrift they\nall were. Just because their challenges couldn’t be easily named didn’t mean\nthey didn’t exist.\n\n“My life as a parent was a battleground for various belief systems,” she\nwrites,[[43]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7945 \"note\") “all of\nwhich had one thing in common: an inability to come to terms with human\nvariability.”\n\nSinger and her family were disabled in a way that no one knew how to name, so\nshe created a name for them: they were _neurodiverse_ , and they suffered\nbecause the world demanded they be _neurotypical_. These terms would be\npopularized by journalist Harvey Blume and widely adopted by disability\nadvocates a few years later. The label _neurodiverse_ includes everyone from\npeople with ADHD, to Down Syndrome, to Obsessive-Compulsive Disorder, to\nBorderline Personality Disorder. It also includes people with brain injuries\nor strokes, people who have been labeled “low intelligence,” and people who\nlack any formal diagnosis, but have been pathologized as “crazy” or\n“incompetent” throughout their lives. As Singer rightly observed,\nneurodiversity isn’t actually about having a specific, catalogued “defect”\nthat the psychiatric establishment has an explanation for. It’s about being\ndifferent in a way others struggle to understand or refuse to accept.\n\n**_Autism is diverse._** Though the neurological and mental features of Autism\ncut across a wide swathe of people, the way it presents is always a bit\ndifferent. In fact, Autistic traits can manifest in downright paradoxical\nways. At times, I can be so intensely focused on a task (such as reading or\nwriting) that the rest of the world entirely drops away. When I’m\nhyperfixating, I fail to notice things like someone speaking to me or smoke\nfilling the room because I forgot to turn the oven off. At other times, I’m an\nanxious and distractible wreck, unable to make my way through a single\nsentence of a book because my pet chinchilla is hopping around in his cage and\nmaking the bars rattle. These two very disparate responses have the same root\ncause: the overexcitability of Autistic people’s neurons and the inconsistent\nway that we filter stimuli (at least compared to allistics). We tend to be\nboth easily disturbed by sound in our environment, and unable to tell when a\nnoise actually merits our attention, at the same\ntime.[[44]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7954 \"note\") I often\nbrute-force my way into paying attention to something by shutting the rest of\nthe world out. I think it’s also likely that lifelong masking has rendered me\nhypervigilant, almost as a trauma response. My sensory system is used to\nscanning the environment, to determine whether I’m alone and thus “safe”\nenough to be myself. Trauma survivors often become hypervigilant, which tends\nto come with intense sensory\nissues.[[45]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7966 \"note\") Some\nresearchers have also theorized that sensory issues in Autistics are, at least\nin part, caused by the anxiety and hypervigilance we experience from living in\na world that doesn’t accommodate us, and often treats us with\nhostility.[[46]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7977 \"note\")\n\nMost people have heard that Autism is a spectrum, and it’s really true: each\nof us has a unique constellation of traits and features, all at various\ndegrees of intensity. Some people are also subclinically Autistic, meaning\nthey might not qualify for an official diagnosis, in the eyes of\npsychiatrists, but share enough struggles and experiences with us that they\nbelong in the community. Relatives of diagnosed Autistic people, for example,\nfrequently are found to exhibit subclinical\ntraits.[[47]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e7988 \"note\") Of\ncourse, what’s considered to be “subclinical” is often more a function of a\nperson’s ability to hold down a job and conform to societal rules than it is a\nreflection of how much they are suffering.\n\n“Everybody is a little bit Autistic,” is a common refrain that masked Autistic\npeople hear when we come out to others. This remark can feel a bit grating to\nhear, because it feels like our experiences are being downplayed. It’s similar\nto when bisexual people get told that “everybody is a little bit bi.” When\nmost people make remarks like these, they’re implying that because our\ndifference is so universal, we can’t actually be oppressed for it, and should\njust shut up about it. However, I do think that when allistic people declare\nthat everyone is a little Autistic, it means they are close to making an\nimportant breakthrough about how mental disorders are defined: why do we\ndeclare some people broken, and others perfectly normal, when they exhibit the\nexact same traits? Where do we draw the line, and why do we even bother doing\nso? If an Autistic person benefits from more flexibility at work, and more\nsocial patience, why not extend those same benefits to everybody? Autistic\npeople are a normal part of humanity, and we have qualities that can be\nobserved in any other non-Autistic human. So yes, everyone is a little bit\nAutistic. That’s all the more reason to broaden our definition of what is\ndeserving of dignity and acceptance.\n\nAutism can appear in any person, regardless of their age, class, gender, race,\nor other disability status. Despite the incredible diversity of Autism and\nAutistic people, the average person (and even many mental health\nprofessionals) has a singular image of Autism in their minds. You might\nsometimes hear this called “typically presenting” Autism, though that’s really\na misnomer. It’s more like _stereotypical_ Autism.\n\n# “Typical” Autism\n\n“Typical” Autism is visible from an early age, and usually results in a\ndiagnosis by the time a child is in early elementary school. Typical Autistics\ndon’t communicate the way neurotypical society wants them to; they might be\nnonverbal or slow to develop speech, and they avoid gazing at other people or\napproaching them. They engage in repetitive behaviors that are recognizable:\nthey rock in place, slap themselves in the head, or yell and chirp. Their\nsensory pain and social overwhelm is near-constant, and they can’t hide how\nprofoundly they’re suffering. Their parents have trouble managing their\nmeltdowns and sensory overloads, seeing these responses as “behavioral\nissues,” or “noncompliance.” They may complain Autism has “stolen” their once\nwell-behaved baby from them. Typical Autistics are probably boys, and they’re\nprobably white, and they are likely to come from wealthy or upper-middle-class\nfamilies who can access diagnosis and therapeutic support (and who tend to\nhave pretty restrictive norms of what constitutes “appropriate” public\nbehavior).\n\nIn reality, typical Autistics aren’t all that typical. The vast majority of\nAutistic people who have been diagnosed flout this incredibly rigid set of\ncriteria in one way or\nanother.[[48]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8002 \"note\") That’s\ndespite the fact all existing diagnostic tools for Autism were developed with\nwealthy, white, gender-conforming boys in mind. When we consider the evidence\nthat Autism is underdiagnosed in girls, Black, indigenous, Asian, and Latinx\npeople,[[49]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8010 \"note\") and\nthose in poverty,[[50]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8024\n\"note\") among other groups, we can see that “typical” Autism is probably even\nless typical than official figures would have us believe.\n\nThe line between “typical” Autism and “atypical” Autism is quite permeable,\nand often has more to do with a person’s position in society than it does the\nsupposed severity of their Autistic traits. Crystal had all the classic\nindicators of Autism: repetitive play, lack of social engagement, self-\nstimulatory behavior, difficulty staying on task at school. But because\nCrystal didn’t look like the “typical” Autistic person, she didn’t register as\ndisabled to most of the world. For all the distress she was in, teachers and\nschool counselors never again raised it as a possibility.\n\n“Report cards called me a joy to have in class, and _sensitive_ ,” she says.\n“Which was a sneaky way of saying they thought I cried too much and got too\nhurt when kids were mean to me. Spacing out in math class wasn’t like, this\nalarming sign I was retreating into a shutdown. I was just a daydreamy girl\nwho cried sometimes, which for a lot of my male teachers was probably their\nfeminine ideal, when you think about it.”\n\nAn _Autistic_ _shutdown_ happens when an Autistic person gets so\noverstimulated and stressed, they can no longer process their\nsurroundings.[[51]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8032 \"note\")\nIt’s the quieter, more interior counterpart to an Autistic _meltdown_ , which\ntends to involve more crying, self-harm, or outward aggression. Shutdowns are\nessentially a way of dissociating from one’s surroundings. It can look like\nfalling asleep very suddenly, becoming unresponsive, or just kind of zoning\nout (which is how it presented in Crystal’s case). Crystal suspects that had\nshe been an Autistic boy, her shutdowns would have been viewed differently.\nBoys are supposed to have agency and confidence, and engage actively with the\nworld. Being nonresponsive and depressed might have inspired early\nintervention, rather than morphing into an unspeakable family secret. Instead,\nCrystal’s parents told her to stop being “so weird” and to sit up and “look\nalive.” When confusion and frustration made her want to break down and cry,\nshe was similarly told to tamp those urges down.\n\n“Getting smaller and asking for nothing was how I kept people from calling me\ntoo sensitive so often,” she says. “That and assuming that if I was bad at\nsomething, it’s because I was never, ever gonna be good at it. Better to not\nask.”\n\nNow that she knows she’s Autistic, Crystal is trying to unlearn these deep-\nseated beliefs about herself. She wants to become someone who doesn’t\napologize for crying, and doesn’t always cope with stress by locking herself\naway from the world. She wants to be able to build a life around the fact that\na twenty- or thirty-hour workweek is the most she can manage. And she wants to\nrelearn math with a nonjudgmental tutor, who’ll explain things to her in a\ndirect, patient way, without any implied meanings or latent sexism.\n\n“Can I look back one day and say to myself, all the things I hate about myself\nare actually my greatest strengths?” She ponders. “I don’t know. Someone\nshould have always been telling me that. But you try to accept what happened.\nI can’t really yet. I’m too pissed.”\n\nLike many people who have only recently figured out they’re Autistic, Crystal\nis still reeling about her newfound identity, and can’t seem to stop thinking\nabout how unfairly she was treated in the past. There’s an entire class of\nAutistic people who are excluded and alienated in these ways, and we’ll get to\nmeet many more of them in the next few chapters. But first, we need to dive\ninto exactly why the image of typical Autism is what it is.\n\n# Why Is Autism Synonymous with White Boys Who Love Trains?\n\nThe Autistic people who wind up needing to mask the most are usually those who\nare undiagnosed due to things like gender, race, or socioeconomic status.\nThese same populations of people also tend to be raised to be more agreeable\nand pleasant than their white male peers. For example, developmental\npsychology research has repeatedly noted that even small acts of play-\naggression in girls are severely discouraged and punished by their teachers\nand parents as “inappropriate.” A girl might be admonished for slamming a\ncouple of toys into one another, for example. Meanwhile, most boys are allowed\nto be rough and sometimes violent in their\nplay.[[52]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8037 \"note\") Because\ngirls are held to a much more restrictive social standard than boys are, they\nlearn to hide any troublesome, “violent,” or disruptive Autism features much\nearlier. Similar dynamics are at play for Autistic people of color and trans\nAutistic people of a variety of identities, as well as other\nmaskers.[[53]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8048 \"note\")\n\nFor a long time, Autism researchers believed the condition was truly less\nsevere and less common in people of color and girls. Today, some still truly\nbelieve “female Autism” is less severe, though most professionals recognize\nthat members of these marginalized groups are simply not given as much social\nlatitude to be strange or disruptive, and that the same qualities are\nperceived differently in a boy than in a\ngirl.[[54]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8062 \"note\") However,\nthe legacy of erasing Autistic girls, trans and gender-nonconforming\nAutistics, and other marginalized populations lingers.\n\nThe idea that Autism is a “boy’s” disorder goes all the way back to when the\ncondition was first described at the turn of the twentieth century. Hans\nAsperger and other early Autism researchers did study girls on the spectrum,\nbut generally left them out of their published research\nreports.[[55]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8074 \"note\")\nAsperger in particular avoided writing about Autistic girls because he wanted\nto present certain intelligent, “high-functioning” Autistic people as\n“valuable” to the Nazis who had taken over Austria and were beginning to\nexterminate disabled people en masse. As Steve Silberman describes in his\nexcellent book _NeuroTribes_ , Hans Asperger wanted to spare the “high\nfunctioning” Autistic boys he’d encountered from being sent to Nazi death\ncamps. Silberman described this fact somewhat sympathetically; Asperger was a\nscientist who had no choice but to collude with the fascist regime and save\nwhat few children he could. However, more recently unearthed documents make it\nclear that Asperger was far more complicit in Nazi exterminations of disabled\nchildren than had been previously\nbelieved.[[56]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8082 \"note\")\nThough Asperger held intelligent, “little professor” type Autistics close to\nhis heart, he knowingly sent more visibly debilitated Autistics to\nextermination centers.\n\nInformed by eugenicist ideals that only granted rights to those who were\n“valuable” to society, Asperger focused on describing Autism as a disorder for\nintelligent, yet troubled boys, usually ones from wealthy families. Girls with\ndisabilities were seen as more disposable, so they were left out of the\nconversation.[[57]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8090 \"note\")\nBlack and brown Autistics weren’t described at all by Asperger or most of his\ncontemporaries, even those who were doing research in more racially diverse\ncountries such as the United States. The existence of LGBTQ and gender\nnonconforming Autistics was similarly ignored. In fact, the developer of the\nfirst therapeutic “treatment” for Autism, Applied Behavioral Analysis therapy,\nwas Ole Ivar Lovaas, who also invented anti-gay conversion\ntherapy.[[58]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8101 \"note\") That\nlegacy still haunts the lives of many LGBTQ Autistics, who often feel out of\nplace both in mainstream queer spaces and in Autism\ngroups.[[59]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8109 \"note\")\n\nSince early published research in both English and German only described\nAutistic boys, some psychiatrists from that era concluded the condition was\ncaused by an “extremely male\nbrain.”[[60]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8123 \"note\")\nAutistic people were supposedly too analytical, too rational, and too\nindividualistic to function in society on their own. This view influenced how\nall the diagnostic guidelines were written, and created a feedback loop that\nendured for decades: the Autistics who got diagnosed were primarily wealthy\nwhite boys, and those boys continued to set the standard of what Autism was\nand how it was understood in the studies that\nfollowed.[[61]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8132 \"note\") The\nfew white girls who were diagnosed had to be very obviously “masculine” in how\ntheir Autism presented. Nonwhite Autistics were instead identified as defiant,\nantisocial, or schizophrenic—all disorders that made it easier to incarcerate\nthem, or forcibly place them in\ninstitutions.[[62]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8140 \"note\")\n\nA century after these trends first began, massive gender- and race-based\ndisparities in Autism diagnoses still exist. For decades, Autistic boys have\noutnumbered girls at a ratio of 4 to\n1.[[63]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8148 \"note\") Girls like\nCrystal are still routinely passed over and denied assessments, because they\nare well-behaved and too pleasant to “really” be Autistic. Autistic trans\npeople and people of color are similarly\nexcluded.[[64]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8162 \"note\") When\nany of us do discover our identities and come out, we risk being told we\n“don’t look Autistic.”\n\nIn media, nearly every Autistic character is a white man with a monotone\nvoice, rude demeanor, and a penchant for science. Think of the irascible\ngenius Rick from _Rick and Morty_\n,[[65]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8173 \"note\") the\nhypercompetent yet cold Shaun Murphy from ABC’s _The Good Doctor_ , or the\nnerdy and condescending Sheldon Cooper from _The Big Bang Theory_. In this\ncultural landscape, there’s little room for Autistics who are sensitive,\nemotionally expressive, artistic, or uninterested in academic success. Autism\nis so broadly associated with assholery that many of us initially hate\nassociating with the term, and try to overcompensate by being excessively\neasygoing and nonconfrontational. It takes many years of research and meeting\nreal-life counter-examples for most of us to recognize Autism isn’t the cold,\nrobotic condition we’ve been told it is.\n\nBeing exposed to these misconceptions and shallow stereotypes can have a\nprofound impact on how Autistic people see ourselves, and which qualities we\naim to mask.\n\nIn the exercise below, I’d like you to ponder what messages about Autism you\nmight’ve absorbed as a child, and how that may have shaped your self-\nperceptions and your mask. For reasons we’ll get into more thoroughly in the\nnext few chapters, an Autistic person’s mask tends to be informed by the\nAutistic qualities they have been trained to hate or fear the most.\n\n# Autism Stereotypes:\n\n## How Have They Affected You?  \n  \n---  \n1\\. Think of some images of Autism that you saw on TV or in movies. If you\ncan, name a few Autistic characters or figures you saw during this time. 2\\.\nPick a few Autistic characters (or characters implied to be Autistic) and\ndescribe them in three to five words. For example, I might describe Dustin\nHoffman’s Rain Man as distant, a genius savant, and helpless.\nCharacter:_____­_____­_____­__ Traits: _____­_____­_____­_____­___\nCharacter:_____­_____­_____­__ Traits: _____­_____­_____­_____­___\nCharacter:_____­_____­_____­__ Traits: _____­_____­_____­_____­___ 3\\.\nComplete the sentence: Before I knew better, I assumed all Autistic people\nwere _______, ________, and _____­_____­. 4\\. In what ways are you different\nfrom these images of Autism? 5\\. Has anyone ever told you that you “don’t look\nAutistic” or that you “can’t be Autistic”? What do you think they meant by\nthat? How did hearing that feel?  \n  \nTo download this chart, go to <http://prhlink.com/9780593235249a001>.\n\nThese days, varied portrayals of Autistic people do exist. Abed Nadir on the\nsitcom _Community_ is a Palestinian Muslim man with a sharp wit and a penchant\nfor movies, as well as the more clichéd chilly demeanor and difficulty\nsmiling. In the popular multiplayer game _Overwatch_ , Symmetra is a confident\nAutistic Indian woman who blasts her opponents with turrets she’s invented.\nBeth Harmon of the Netflix series _The Queen’s Gambit_ is a beautiful,\nsubstance-addicted chess player, and is heavily implied to be Autistic. I only\nstarted seeing characters like these when I was in my late twenties, after I\nalready knew I was Autistic, had met a variety of Autistic people in real\nlife, and began seeking representation that went beyond the tortured white\ngenius image. Diversifying and deepening my knowledge of what Autism could be\nwas absolutely essential to understanding myself and slowly beginning to build\nself-love and acceptance. For many of the masked Autistic people I interviewed\nfor this book, meeting a variety of mold-breaking, “atypical” Autistics of\nmany different backgrounds was similarly important.\n\n# Suspect You’re Autistic?\n\nMasked Autistic people are basically everywhere, though by our very nature\nwe’re socially invisible. You can find us in any number of fields people might\nnot associate with stereotypically Autistic behavior, including sales, the\nservice industry, and the arts. Because so many of us mask through inhibition\nand withdrawal, we might not stand out as socially awkward, at least not in a\nway anyone can pinpoint. Though many of us experience sensory issues, anxiety,\nmeltdowns, and debilitating mental health symptoms, we push as much of that\nmisery into the private realm as possible. Our elaborate veils of coping\nmechanisms and camouflaging can create the illusion we don’t need help. Often\nthis comes at the expense of giving up on the areas of life where we might\nneed assistance. We may eschew relationships, drop out of grueling academic\nprograms, avoid working in fields that require networking and socializing, or\ncompletely disengage from activities that involve using our bodies, because we\nfeel so detached and uncoordinated in them. Most of us are haunted by the\nsense there’s something “wrong” or “missing” in our lives—that we’re\nsacrificing far more of ourselves than other people in order to get by and\nreceiving far less in return.\n\nDue to the fact that Autism is so severely underdiagnosed, it’s hard to\nestimate just how prevalent the neurotype really is. We do know that as public\nawareness of Autism has increased, and as diagnosis procedures have gotten a\ntiny bit less biased, the diagnosis rate has continually gone up. As of 2020,\none in 54 children is diagnosed as Autistic, up from one in 68 just four years\nago. In the 1990s only one in every 2,500 children was\ndiagnosed.[[66]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8179 \"note\") This\nupward trend shows no sign of stopping, as all evidence suggests the condition\nis still profoundly underrecognized in women, trans people, Black and brown\npeople, people in poverty, and those without access to screening and therapy.\nIn the United States, as many as 50 percent of all people who need mental\nhealth support lack access to\nit,[[67]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8187 \"note\") so we are\ntalking about a truly massive underdiagnosis rate.\n\n*Source: Centers for Disease Control and Prevention (CDC)\n\nFrom all this data, we can assume that at least half of all Autistic people in\nthe United States currently fail to get diagnosed. That’s a conservative\nestimate, based on the assumption that every Autistic person with access to\ntherapy gets an accurate diagnosis, a fact we know not to be true. It’s also\nworth bearing in mind that Autism runs in families, and that for every\ndiagnosed Autistic child reflected in that chart, there’s probably several\nother relatives who exhibited Autism spectrum traits. In my own family, almost\neveryone has some Autistic traits and can be considered a part of the Autism\ncommunity, even if some might not qualify based on an official assessment or\nmight not be interested in identifying as\ndisabled.[[68]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8195 \"note\")\n\nIf you’re reading this book, you probably suspect that you or someone you know\nis a masked Autistic, or otherwise neurodiverse. I have been writing about my\nown journey of Autistic self-discovery for many years now, and every single\ntime I post online about it, I’m inundated with messages from people who are\nquestioning whether they’re on the spectrum, and want my advice on how to find\nout. Usually, their first question is how to get tested for Autism Spectrum\nDisorder. My initial response to that is to present them with three questions:\n\n  1. Do you have health insurance that covers Autism assessments?\n\n  2. Can you find an Autism assessment specialist in your area who has a proven track record of working successfully with Autistic adults?\n\n  3. What do you hope to get out of a formal diagnosis?\n\nThe first and second questions can prove quite dispiriting to answer. In the\nUnited States, many health insurance plans do not cover Autism assessment in\nadults.[[69]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8206 \"note\") A\nlimited number of specialists are qualified to assess and diagnose Autism\n(your average psychologist can’t do it), and the diagnostic process typically\ninvolves multiple tests, screening surveys, and even interviews with the\nAutistic person’s family and friends. Without insurance coverage, this process\ncan cost anywhere from\n$1,200[[70]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8214 \"note\") to\n$5,000.[[71]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8222 \"note\")\n\nEven when a person can afford to be assessed, identifying a specialist who\nknows how to diagnose Autistic adults can be prohibitively difficult. My\nfriend Seb (who’s in their mid-twenties) sought out an assessment in the UK\nand was subjected to tests clearly designed for small kids. A therapist asked\nSeb to arrange various toys on a table and make up stories about them (this is\npart of a common diagnostic tool called the Autism Diagnostic Observation\nSchedule, or the ADOS, and it was developed for use in\nchildren).[[72]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8230 \"note\") A\nquestionnaire was given to Seb’s mother to fill out, and Seb wasn’t permitted\nto look at what she’d said. They were completely disempowered by the whole\nprocess. Some people whom I interviewed for this book reported being turned\naway by multiple assessors, for things as simple as being a woman, dressing\nwell, or having voices that weren’t completely monotonous. Sometimes assessors\ndecide to give adults labels they view as less stigmatizing, such as nonverbal\nlearning disorder, rather than identifying them as Autistic explicitly.\n\n“I had to see two specialists,” Crystal tells me. “The first one said\nbasically the same thing my grandpa used to say: girls usually aren’t\nAutistic. You’re doing fine in life. Don’t worry about it.”\n\nTo this day, a majority of Autism assessment tools are based on the decades-\nold ones developed for white male children from wealthy and middle-class\nfamilies.[[73]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8238 \"note\") With\nyears of clinical experience, some experts learn to recognize Autism in those\nwho mask. They may know, for example, that masked Autistics can make eye\ncontact, though many of us stare too strongly by neurotypical standards, or\nfor too long. They might understand that Autistic women and people of color\nhave to appear friendly as a means of survival, so their tone of voice might\nnot be totally flat. Perhaps they’re even aware of Autism’s link with\nsubstance addictions and eating disorders, particularly among people who have\nto fake neurotypicality all day long at their jobs. However, these facts are\nnot a core part of how assessors are trained, and many spend their entire\ncareers reinforcing old sexist, white supremacist notions of how the\ndisability looks.\n\nThis brings me to my third question: what do you hope to get out of being\nformally diagnosed? It can come with serious social and legal benefits under\nthe Americans with Disabilities Act (and laws in other countries like it), and\nother antidiscrimination statutes worldwide. You might hope that people will\ntake your problems more seriously when a psychiatrist has validated them. A\nformal diagnosis means you can receive disability accommodations at school or\nwork, and you can pursue a legal case if an employer or landlord shows\ndocumentable signs of bias against you. In some places a diagnosis can qualify\nyou for a medical marijuana card, or a therapy animal. Family members who have\ntold you that you’re whiny and lazy may finally get off your case when they\nrealize you have a developmental disorder. A therapist or medical care\nprovider may tailor their treatment of you to your neurotype. These are the\nkinds of outcomes many neurodivergent people hope for when they pursue formal\nrecognition.\n\nUnfortunately, a diagnosis is not a guarantee you will receive any of these\nbenefits. Proving in a court of law that you’ve been discriminated against as\nan Autistic person requires extensive\ndocumentation[[74]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8246 \"note\")\nand is prohibitively expensive to pursue for most disabled people. Even though\na diagnosed disability entitles you to accommodations on paper, many employers\nand educators refuse to provide them, or mistreat the employees and students\nwho request them (for more on the limitations of the ADA and its inconsistent\nenforcement, see Chapter 8). And as much as I’d like to promise that being\nrecognized formally as an Autistic will get judgmental friends and family off\nyour back, I’ve heard too many counter-examples to claim that’s really the\ncase. Your family members may find your disability even more threatening once\nit’s validated by a doctor, or they might use your diagnosis to undermine your\njudgment or infantilize you. This isn’t intended to dissuade you from seeking\na diagnosis; I just don’t want anyone to have the impression that a piece of\npaper signed by a psychiatrist magically unlocks a suite of resources and\nsocial respect.\n\nAdditionally, an Autism diagnosis does not grant you access to any particular\ntherapy or medication, because there are no evidence-based treatments for\nAutism in adults. Most therapists are not trained to work with Autistic\nadults, and many of them harbor very shallow, outdated understandings of what\nthe neurotype is. Even those who do specialize in Autism are usually trained\nprimarily in working with Autistic kids, “helping” them to behave in a more\nagreeable, passive fashion. Here in Chicago, I’m aware of just one therapist\nwho is competent in treating Autistic adults who mask, and the only reason I\nknow they’re competent is that other Autistic people have vouched for them to\nme. I do know several mental health providers in other cities who have\nconfessed to me privately that they are Autistic, and love working with fellow\nAutistic patients. However, each of them has told me they cannot openly\nidentify as Autistic professionally. There’s too great a risk that their\ncolleagues would view them as incompetent or unprofessional if they were open\nabout their neurodivergence.\n\nOf course, even the idea of pursuing a treatment “for” Autism is predicated on\nthe idea we are broken or sick. This is an idea the neurodiversity movement\ncompletely rejects. There is no medication for Autism, no cure for it, and no\nway of changing one’s neurotype. As a community, most Autistics oppose\nattempts to “fix” us. There are some modifications that can be made to\nexisting therapeutic methods, to make them a better fit for Autistic adults,\nbut unless a provider takes the time to self-educate, they may be unaware such\nmodified treatments exist. For the most part, learning you’re Autistic is a\njourney of self-acceptance, community building, and growing self-advocacy, and\nyou might not need or want a diagnosis to go down that path.\n\nFor all the reasons outlined above, I firmly support Autistic self-\ndetermination. I prefer the terms _self-determination_ or _self-realization_\nto _self-diagnosis,_ because I believe it’s more sensible to view Autistic\nidentity through a social lens than a strictly medical\none.[[75]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8254 \"note\") Diagnosis\nis a gatekeeping process, and it slams its heavy bars in the face of anyone\nwho is too poor, too busy, too Black, too feminine, too queer, and too gender\nnonconforming, among others. The Autistics who lack access to fair diagnoses\nneed solidarity and justice the most desperately out of all of us, and we\ncan’t just shut them out.\n\nThough people like Crystal often regret having not been assessed for Autism at\na young age, Autistic children who _are_ diagnosed when they are young\nexperience both greater access to resources, and more intense,\ninstitutionalized stigma. Being identified formally as disabled is very much a\ndouble-edged sword; a diagnosis can even be used against you in divorce\nproceedings or child custody cases, or to force a legal adult under a\nfinancial conservatorship. This doesn’t mean I would recommend against\npursuing diagnosis in all cases. I know masked Autistic parents who are very\nglad their Autistic children got assessed and diagnosed when they were young.\nFor many Autistic parents, it’s the diagnosis of their children that kicks off\ntheir own exploration of an Autistic identity. Having a recognized diagnosis\nof Autism in the family can also ensure that professionals take your suspicion\nyou’re Autistic more seriously (that certainly has been true in my case).\n\nThe parents I know who have had a positive experience with assessment entered\nthe diagnostic process recognizing they would need to fight many battles to\nhave their child’s agency and humanity respected. This is true of the adults\nwho have successfully pursued formal diagnosis for themselves as well.\nUnfortunately, Autistic people are frequently put in the position of having to\neducate our own health care providers. Autistic children in particular need\nstrong advocates in their corner, fighting to make sure their boundaries are\nrespected and that any treatment they are given is actually in their best\ninterest. If you wish to get diagnosed, or wish for your child to be, you\nshould go into the process with accurate expectations, armed with as much\ninformation as possible, and ready to fight or switch providers multiple times\nif needed.\n\nIf you don’t wish to brave the long, arduous, and often expensive process of\nbeing assessed, you do not have to. Medical documentation does not make your\nexperience any more real. Self-realized Autistics are not lesser members of\nthe community. In most Autistic self-advocacy spaces I frequent, I have no\nidea who is diagnosed and who is not, because it truly does not matter.\n\nI believe that Autistic people have the right to define who we are, and that\nself-definition is a means of reclaiming our power from the medical\nestablishment that has long sought to corral and control us. Our deviance from\nthe norm doesn’t have to be the core part of how we understand ourselves. We\ncan push for social norms to be widened, until we reach the point that Autism\nis viewed as a neutral fact about a person’s being, on par with needing\nglasses or having freckles. As we make major gains in public awareness and\nadvocacy, we will begin to occupy a less disabled position in society. But\nwe’ll still all be Autistic. Accordingly, we shouldn’t let the view of Autism\nas an impediment shape how we see ourselves or determine who belongs among us.\n\n# A Few Notes on Terminology\n\nThroughout this book, I capitalize “Autistic” for the same reason members of\nthe Deaf community capitalize “Deaf”—to indicate it is a part of my identity I\nam proud of, and to signal Autistics have our own culture, history, and\ncommunity. Since Eugen Bleuler first coined the word in the early 1900s,\nAutism has largely been used in negative and dehumanizing ways, and to this\nday many parents and educators are still deeply frightened by it. By\ncapitalizing Autism, I signal that it’s actually an important, meaningful\naspect of who we are, one we don’t need to shy away from.\n\nThroughout, I will also refer to Autism as a disability. _Disability_ is not a\nbad word, because being disabled is not a shameful thing. We are not\n“differently abled”—we are disabled, robbed of empowerment and agency in a\nworld that is not built for us. “Differently abled,” “handi-capable,” and\nsimilar euphemisms were created in the 1980s by the abled parents of disabled\nchildren, who wished to minimize their children’s marginalized status. These\nterms were popularized further by\npoliticians[[76]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8268 \"note\") who\nsimilarly felt uncomfortable acknowledging disabled people’s actual\nexperiences of\noppression.[[77]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8278 \"note\")\nThese words obscure reality and reflect a discomfort many people have with\ndisabled bodies and brains. A person who is completely blind is not\n“differently sighted”—they lack an ability that other people have, in a world\nthat was designed by and for people who can see. The world actively _dis-\nables_ people by failing to provide accommodations they need. Naming the\nreality of disability shows respect for disabled people and awareness of how\nwe are oppressed. “Differently abled” attempts to erase that behind a cutesy\neuphemism, and many of us find the term offensive.\n\nIn a similar vein, I almost always will use “Autistic” and not “person with\nAutism.” Many non-disabled parents of Autistic kids prefer what’s called\n“person first” language rather than “disability first” or “identity first”\nlanguage.[[78]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8289 \"note\")\nDisability service organizations that are not run by disabled people tend to\nadvocate for person first language as well. I also know many clinicians and\nsocial workers who tell me that when they were in school, they were taught to\nalways separate a person’s disability from their identity in this way.\n\nWhen people use person-first language, they often say it’s because they don’t\nwant disabled people to be defined by their disability. However, phrases like\n“person with Autism” distance a person’s disabled status from their humanity\nin a way that can be quite harmful. Autism is not a thing that is added on to\na person—it’s integral to their life and cannot be removed from who they are.\nWe don’t call Asian people “people with Asianness” and we don’t call gay folks\n“people with homosexuality” because we recognize it is respectful to view\nthese identities as parts of their personhood. Language such as “identifies as\nAutistic” can also come across as dubious. If I really respect a trans woman’s\ngender, for example, I wouldn’t say “this person identifies as a woman.” I’d\nsimply say, “she’s a woman” and leave it at that.\n\nThe vast majority of Autism self-advocates prefer identity-first language and\ndislike euphemisms like “special” and “differently abled,” for all the reasons\nI’ve outlined here. They also discourage describing a person as “high” or\n“low” functioning, preferring instead things like “high support needs.” Here’s\na table summarizing some of the most common terminology preferences expressed\nby the community:\n\n# Autism Terminology:  \nCommon Dos and Don’ts  \n  \n---  \n  \n# Use This\n\n|\n\n# Avoid This  \n  \nAutistic person Autist Autistic On the Autism spectrum |  Person with Autism  \nIs Autistic |  Identifies as having autism  \nIs disabled Has a disability |  “Special needs” “Differently abled” “Handi-capable”  \nNeurotypical (NT) Allistic Non-Autistic |  Normal  \nHas high support needs Has low support needs |  Low functioning High functioning  \nMasked Autism |  Female Autism Asperger’s High-functioning Autism  \nNonverbal Loses speech |  Mute Dumb  \nIntellectually disabled Developmentally disabled |  R*tarded Stupid “Special”  \nDirect language about what a person can or can’t do, and what kind of support they need |  Euphemisms, language that minimizes challenges, language that belittles or condescends  \n  \nAutistics are a diverse group, though, and we don’t all have to agree on which\nterms we like and dislike having used for ourselves. If you are Autistic, you\nget to decide what language works best for you. Some people prefer to say they\nare “on the spectrum,” for example, rather than strictly Autistic. Others\nidentify as having Asperger’s, though that disorder label no longer exists,\nand was rooted in Hans Asperger’s eugenicist\nresearch.[[79]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8297 \"note\") I\nrecognize that people who had that term forced on them in the past may feel an\nattachment to it, or a desire to reclaim it. The word _bisexual_ was once a\nmental illness label,[[80]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8305\n\"note\") but we don’t tell bisexual people they can’t use it because of its\noffensive history. When someone like folklorist Anand Prahlad writes a book\nlike _The Secret Life of a Black Aspie,_ it’s clear his use of the term\n“Aspergers” is not intended to reinforce old, white supremacist notions of\nwhat the disability is. I find it’s far more important to question the belief\nthat supposedly “higher functioning” Autistic lives matter more than others\nthan it is to scrub all people’s language of outdated or problematic terms.\nAdditionally, it is vital that the disability self-advocacy community remain\naccessible to all people of all ability levels. That requires we extend grace\nand understanding to people who don’t communicate exactly the way we might\nlike them to.\n\nThough most of the community discourages the use of such terms, some Autistic\npeople do identify as “low functioning” or “severely Autistic.” Functioning\nlabels oversimplify the Autistic experience, and they do serve to imply that\nwe should be defined by how productive and independent we are. That’s a big\nproblem. At the same time, function labels can occasionally be used to\nhighlight the fact that those of us who can talk, dress ourselves, or hide our\nmeltdowns have social privileges other Autistic people do not have. I don’t\nfunction “highly” in every single realm of my life, but I am able to get by\nmore easily than many other Autistics. My acceptance in society is conditional\non my behaving respectably and being productive. That’s really a deeply\nableist reality, but I shouldn’t pretend it isn’t true. Though having to mask\nas a desirable, respectable person can be very soul-crushing, it does protect\nme from physical violence, institutionalization, poverty, and loneliness. I\ncan understand why my friend Angel believes it’s worth pointing out that his\nlife as a nonspeaking person with intellectual disabilities is really\ndifferent from mine. Angel says he is low functioning, and says that he has\nsevere Autism; though some in our community find that offensive, I stand by\nhis right to name his own experience.\n\nI love that every Autistic person has their own unique relationship to these\nlabels, and their own thoughts. Our disagreements show that the Autistic\ncommunity is diverse, filled with people who form their own opinions and speak\ntheir minds. We’re not a monolithic group, and our individual journeys shape\nhow we express our identities to the world. I’ve done my best in this book to\nhonor the terminology each individual Autistic person uses for themselves.\nThis means that sometimes I’ll call someone a “person with Autism” or a “low-\nfunctioning” person, even though self-advocacy groups have good reasons to\ndiscourage allistics from using such words thoughtlessly. If someone self-\nidentifies as an Aspie or as having Asperger’s, I’ll accurately reflect that\nas well. I hope that even if you have specific stances on which terms you like\nand dislike, you can respect my interview subjects’ agency to name themselves,\nas I have strived to do.\n\n"
      }
    ]
  }
]

---

### Assistant
> 12/1/2025, 1:49:10 PM

[
  {
    "type": "tool_use",
    "id": "toolu_01AJ6UjZX2j1VpoRwQisYXYW",
    "name": "mcp__ebook-mcp__get_epub_chapter_markdown",
    "input": {
      "epub_path": "/home/chris/dev/projects/codex/brain_explore/books/Taking Charge of Adult ADHD Second Edition.epub",
      "chapter_id": "text/part0016_split_000.html#F8900-ccc77842d77249eb8d63b72d3693c8e9"
    }
  }
]

---

### User
> 12/1/2025, 1:49:10 PM

[
  {
    "type": "tool_result",
    "content": "Error executing tool get_epub_chapter_markdown: Anchor F8900-ccc77842d77249eb8d63b72d3693c8e9 not found in text/part0016_split_000.html",
    "is_error": true,
    "tool_use_id": "toolu_01AJ6UjZX2j1VpoRwQisYXYW"
  }
]

---

### Assistant
> 12/1/2025, 1:49:14 PM

[
  {
    "type": "text",
    "text": "Let me try a different approach and look at the Executive Functions book by Barkley which is also available:"
  }
]

---

### Assistant
> 12/1/2025, 1:49:15 PM

[
  {
    "type": "tool_use",
    "id": "toolu_015f1tD9ETtKSfsEUGUqTKrh",
    "name": "mcp__ebook-mcp__get_epub_toc",
    "input": {
      "epub_path": "/home/chris/dev/projects/codex/brain_explore/books/Executive Functions - Russell Barkley.epub"
    }
  }
]

---

### User
> 12/1/2025, 1:49:15 PM

[
  {
    "tool_use_id": "toolu_015f1tD9ETtKSfsEUGUqTKrh",
    "type": "tool_result",
    "content": [
      {
        "type": "text",
        "text": "Selected Works by Russell A. Barkley"
      },
      {
        "type": "text",
        "text": "text/part0000.html#0-5d925f0406034e71a7cb0da677792046"
      },
      {
        "type": "text",
        "text": "Title Page"
      },
      {
        "type": "text",
        "text": "text/part0001.html#UGI0-5d925f0406034e71a7cb0da677792046"
      },
      {
        "type": "text",
        "text": "Copyright Page"
      },
      {
        "type": "text",
        "text": "text/part0002.html#1T140-5d925f0406034e71a7cb0da677792046"
      },
      {
        "type": "text",
        "text": "Dedication"
      },
      {
        "type": "text",
        "text": "text/part0003.html#2RHM0-5d925f0406034e71a7cb0da677792046"
      },
      {
        "type": "text",
        "text": "About the Author"
      },
      {
        "type": "text",
        "text": "text/part0004.html#3Q280-5d925f0406034e71a7cb0da677792046"
      },
      {
        "type": "text",
        "text": "Acknowledgments"
      },
      {
        "type": "text",
        "text": "text/part0005.html#4OIQ0-5d925f0406034e71a7cb0da677792046"
      },
      {
        "type": "text",
        "text": "Contents"
      },
      {
        "type": "text",
        "text": "text/part0006.html#5N3C0-5d925f0406034e71a7cb0da677792046"
      },
      {
        "type": "text",
        "text": "1. Problems with the Concept of Executive Functioning"
      },
      {
        "type": "text",
        "text": "text/part0007.html#6LJU0-5d925f0406034e71a7cb0da677792046"
      },
      {
        "type": "text",
        "text": "What Is EF?: The Lack of an Operational Definition"
      },
      {
        "type": "text",
        "text": "text/part0007.html#h1-1"
      },
      {
        "type": "text",
        "text": "How Is EF Assessed?: The Poor Ecological Validity of Psychometric Tests of EF"
      },
      {
        "type": "text",
        "text": "text/part0007.html#h1-2"
      },
      {
        "type": "text",
        "text": "How Does EF Work?: The Limitations of Current Cognitive Models of EF"
      },
      {
        "type": "text",
        "text": "text/part0007.html#h1-3"
      },
      {
        "type": "text",
        "text": "Why EF?: The Importance of Evolution in the Origins and Purposes of EF"
      },
      {
        "type": "text",
        "text": "text/part0007.html#h1-4"
      },
      {
        "type": "text",
        "text": "Conclusions and Specific Aims"
      },
      {
        "type": "text",
        "text": "text/part0007.html#h1-5"
      },
      {
        "type": "text",
        "text": "2. The Extended Phenotype: A Foundation for Modeling Executive Functioning"
      },
      {
        "type": "text",
        "text": "text/part0008.html#7K4G0-5d925f0406034e71a7cb0da677792046"
      },
      {
        "type": "text",
        "text": "The Conventional View of the Phenotype"
      },
      {
        "type": "text",
        "text": "text/part0008.html#h1-6"
      },
      {
        "type": "text",
        "text": "An Extended Phenotype"
      },
      {
        "type": "text",
        "text": "text/part0008.html#h1-7"
      },
      {
        "type": "text",
        "text": "How Long Is the Reach of the Genes?: The Boundary of the Extended Phenotype"
      },
      {
        "type": "text",
        "text": "text/part0008.html#h1-8"
      },
      {
        "type": "text",
        "text": "The Role of Universal Darwinism in the Human Extended Phenotype"
      },
      {
        "type": "text",
        "text": "text/part0008.html#h1-9"
      },
      {
        "type": "text",
        "text": "Conclusions"
      },
      {
        "type": "text",
        "text": "text/part0008.html#h1-10"
      },
      {
        "type": "text",
        "text": "3. Executive Functioning as an Extended Phenotype"
      },
      {
        "type": "text",
        "text": "text/part0009.html#8IL20-5d925f0406034e71a7cb0da677792046"
      },
      {
        "type": "text",
        "text": "A More Precise Definition of EF"
      },
      {
        "type": "text",
        "text": "text/part0009.html#h1-11"
      },
      {
        "type": "text",
        "text": "An Overview of the EF Extended Phenotype"
      },
      {
        "type": "text",
        "text": "text/part0009.html#h1-12"
      },
      {
        "type": "text",
        "text": "Eight Emerging Developmental Capacities Arising from EF"
      },
      {
        "type": "text",
        "text": "text/part0009.html#h1-13"
      },
      {
        "type": "text",
        "text": "The Pre-Executive Levels and Zones"
      },
      {
        "type": "text",
        "text": "text/part0009.html#h1-14"
      },
      {
        "type": "text",
        "text": "4. The Instrumental–Self-Directed Level"
      },
      {
        "type": "text",
        "text": "text/part0010.html#9H5K0-5d925f0406034e71a7cb0da677792046"
      },
      {
        "type": "text",
        "text": "EF in Six Self-Directed Acts"
      },
      {
        "type": "text",
        "text": "text/part0010.html#h1-15"
      },
      {
        "type": "text",
        "text": "The Importance of Time in EF/SR"
      },
      {
        "type": "text",
        "text": "text/part0010.html#h1-16"
      },
      {
        "type": "text",
        "text": "EF/SR Relies on a Limited Resource Pool"
      },
      {
        "type": "text",
        "text": "text/part0010.html#h1-17"
      },
      {
        "type": "text",
        "text": "Are All Self-Directed Actions EF?"
      },
      {
        "type": "text",
        "text": "text/part0010.html#h1-18"
      },
      {
        "type": "text",
        "text": "How Does EF Govern the Automatic Pre-Executive Level of Behavior?"
      },
      {
        "type": "text",
        "text": "text/part0010.html#h1-19"
      },
      {
        "type": "text",
        "text": "Viewing EF/SR as a System of Feedback Loops"
      },
      {
        "type": "text",
        "text": "text/part0010.html#h1-20"
      },
      {
        "type": "text",
        "text": "Evolutionary and Developmental Considerations"
      },
      {
        "type": "text",
        "text": "text/part0010.html#h1-21"
      },
      {
        "type": "text",
        "text": "Shifting Sources of Control of Human Behavior"
      },
      {
        "type": "text",
        "text": "text/part0010.html#h1-22"
      },
      {
        "type": "text",
        "text": "Conclusions"
      },
      {
        "type": "text",
        "text": "text/part0010.html#h1-23"
      },
      {
        "type": "text",
        "text": "5. The Methodical–Self-Reliant Level"
      },
      {
        "type": "text",
        "text": "text/part0011.html#AFM60-5d925f0406034e71a7cb0da677792046"
      },
      {
        "type": "text",
        "text": "Distinguishing Executive Cognition from Executive Action"
      },
      {
        "type": "text",
        "text": "text/part0011.html#h1-24"
      },
      {
        "type": "text",
        "text": "Using the Physical Environment to Boost EF"
      },
      {
        "type": "text",
        "text": "text/part0011.html#h1-25"
      },
      {
        "type": "text",
        "text": "Social Problems That Likely Contributed to the Evolution of the Self-Reliant EF Level"
      },
      {
        "type": "text",
        "text": "text/part0011.html#h1-26"
      },
      {
        "type": "text",
        "text": "Dimensions of EF Evident in Daily Life Activities"
      },
      {
        "type": "text",
        "text": "text/part0011.html#h1-27"
      },
      {
        "type": "text",
        "text": "EF as Human Reasoning and as the Source of Culture"
      },
      {
        "type": "text",
        "text": "text/part0011.html#h1-28"
      },
      {
        "type": "text",
        "text": "Conclusions"
      },
      {
        "type": "text",
        "text": "text/part0011.html#h1-29"
      },
      {
        "type": "text",
        "text": "6. The Tactical–Reciprocal Level"
      },
      {
        "type": "text",
        "text": "text/part0012.html#BE6O0-5d925f0406034e71a7cb0da677792046"
      },
      {
        "type": "text",
        "text": "Social Reciprocity as a Major Activity of the Extended EF Phenotype"
      },
      {
        "type": "text",
        "text": "text/part0012.html#h1-30"
      },
      {
        "type": "text",
        "text": "The Special Conditions Needed to Support Reciprocity"
      },
      {
        "type": "text",
        "text": "text/part0012.html#h1-31"
      },
      {
        "type": "text",
        "text": "EF, Reciprocity, and Economics"
      },
      {
        "type": "text",
        "text": "text/part0012.html#h1-32"
      },
      {
        "type": "text",
        "text": "Reciprocity, Morality, and Ethics"
      },
      {
        "type": "text",
        "text": "text/part0012.html#h1-33"
      },
      {
        "type": "text",
        "text": "Using Each Other for Mutual Self-Regulation"
      },
      {
        "type": "text",
        "text": "text/part0012.html#h1-34"
      },
      {
        "type": "text",
        "text": "The Role of Parenting and Culture in Reciprocity"
      },
      {
        "type": "text",
        "text": "text/part0012.html#h1-35"
      },
      {
        "type": "text",
        "text": "Implications for EF Tests"
      },
      {
        "type": "text",
        "text": "text/part0012.html#h1-36"
      },
      {
        "type": "text",
        "text": "Conclusions"
      },
      {
        "type": "text",
        "text": "text/part0012.html#h1-37"
      },
      {
        "type": "text",
        "text": "7. The Strategic–Cooperative Level"
      },
      {
        "type": "text",
        "text": "text/part0013.html#CCNA0-5d925f0406034e71a7cb0da677792046"
      },
      {
        "type": "text",
        "text": "The Advent of Social Cooperation in the Extended EF Phenotype"
      },
      {
        "type": "text",
        "text": "text/part0013.html#h1-38"
      },
      {
        "type": "text",
        "text": "Conditions Necessary for Cooperation to Arise"
      },
      {
        "type": "text",
        "text": "text/part0013.html#h1-39"
      },
      {
        "type": "text",
        "text": "The Importance of Division of Labor to a Cooperative"
      },
      {
        "type": "text",
        "text": "text/part0013.html#h1-40"
      },
      {
        "type": "text",
        "text": "The Profound Role of Culture in Cooperatives"
      },
      {
        "type": "text",
        "text": "text/part0013.html#h1-41"
      },
      {
        "type": "text",
        "text": "A Second Possible Stage to the Strategic–Cooperative Level: Principled–Mutualistic"
      },
      {
        "type": "text",
        "text": "text/part0013.html#h1-42"
      },
      {
        "type": "text",
        "text": "Does Religion Have a Role in the Origins of Social Cooperatives and Mutualism?"
      },
      {
        "type": "text",
        "text": "text/part0013.html#h1-43"
      },
      {
        "type": "text",
        "text": "Conclusions"
      },
      {
        "type": "text",
        "text": "text/part0013.html#h1-44"
      },
      {
        "type": "text",
        "text": "8. The Extended Utilitarian Zone"
      },
      {
        "type": "text",
        "text": "text/part0014.html#DB7S0-5d925f0406034e71a7cb0da677792046"
      },
      {
        "type": "text",
        "text": "Objective Means of Judging Extended EF Phenotypic Effects"
      },
      {
        "type": "text",
        "text": "text/part0014.html#h1-45"
      },
      {
        "type": "text",
        "text": "Conclusions"
      },
      {
        "type": "text",
        "text": "text/part0014.html#h1-46"
      },
      {
        "type": "text",
        "text": "9. Implications for Understanding Executive Functioning and Its Disorders"
      },
      {
        "type": "text",
        "text": "text/part0015.html#E9OE0-5d925f0406034e71a7cb0da677792046"
      },
      {
        "type": "text",
        "text": "The Problem of Defining EF"
      },
      {
        "type": "text",
        "text": "text/part0015.html#h1-47"
      },
      {
        "type": "text",
        "text": "The Problem of the Nature of EF: Incomplete Theories"
      },
      {
        "type": "text",
        "text": "text/part0015.html#h1-48"
      },
      {
        "type": "text",
        "text": "The Problem of “Why EF?”"
      },
      {
        "type": "text",
        "text": "text/part0015.html#h1-49"
      },
      {
        "type": "text",
        "text": "Conclusions"
      },
      {
        "type": "text",
        "text": "text/part0015.html#h1-50"
      },
      {
        "type": "text",
        "text": "10. Implications for the Assessment and Clinical Management of Deficits in Executive Functioning"
      },
      {
        "type": "text",
        "text": "text/part0016.html#F8900-5d925f0406034e71a7cb0da677792046"
      },
      {
        "type": "text",
        "text": "The Problem of How to Assess EF"
      },
      {
        "type": "text",
        "text": "text/part0016.html#h1-51"
      },
      {
        "type": "text",
        "text": "Implications for the Clinical Management of EF Deficits"
      },
      {
        "type": "text",
        "text": "text/part0016.html#h1-52"
      },
      {
        "type": "text",
        "text": "Conclusions"
      },
      {
        "type": "text",
        "text": "text/part0016.html#h1-53"
      },
      {
        "type": "text",
        "text": "References"
      },
      {
        "type": "text",
        "text": "text/part0017.html#G6PI0-5d925f0406034e71a7cb0da677792046"
      },
      {
        "type": "text",
        "text": "Index"
      },
      {
        "type": "text",
        "text": "text/part0018.html#H5A40-5d925f0406034e71a7cb0da677792046"
      },
      {
        "type": "text",
        "text": "About Guilford Publications"
      },
      {
        "type": "text",
        "text": "text/part0019.html#I3QM0-5d925f0406034e71a7cb0da677792046"
      },
      {
        "type": "text",
        "text": "Discover More Guilford Titles"
      },
      {
        "type": "text",
        "text": "text/part0020.html#J2B80-5d925f0406034e71a7cb0da677792046"
      }
    ]
  }
]

---

### Assistant
> 12/1/2025, 1:49:20 PM

[
  {
    "type": "text",
    "text": "I've successfully read the first chapter of \"Unmasking Autism\" which provides excellent foundational material. Now let me read more chapters from both books to gather comprehensive information on ADHD dimensions and individual variation. Let me continue with more chapters:"
  }
]

---

### Assistant
> 12/1/2025, 1:49:22 PM

[
  {
    "type": "tool_use",
    "id": "toolu_01DMe87WwXSUxg19L7AQUq6e",
    "name": "mcp__ebook-mcp__get_epub_chapter_markdown",
    "input": {
      "epub_path": "/home/chris/dev/projects/codex/brain_explore/books/Unmasking Autism.epub",
      "chapter_id": "xhtml/Pric_9780593235249_epub3_c002_r1.xhtml"
    }
  }
]

---

### Assistant
> 12/1/2025, 1:49:22 PM

[
  {
    "type": "tool_use",
    "id": "toolu_012Mvg8BAaFZCpYZHUXYZdb5",
    "name": "mcp__ebook-mcp__get_epub_chapter_markdown",
    "input": {
      "epub_path": "/home/chris/dev/projects/codex/brain_explore/books/Unmasking Autism.epub",
      "chapter_id": "xhtml/Pric_9780593235249_epub3_c003_r1.xhtml"
    }
  }
]

---

### User
> 12/1/2025, 1:49:24 PM

[
  {
    "tool_use_id": "toolu_01DMe87WwXSUxg19L7AQUq6e",
    "type": "tool_result",
    "content": [
      {
        "type": "text",
        "text": "# CHAPTER 2\n\n# Who Are the Masked Autistics?\n\nBobbi, an Autistic nonbinary person in their mid-thirties, says, “I wasn’t\nraised or ‘socialized’ as an Autistic girl. I was raised as a weird kid, and a\ngender failure.”\n\nBobbi says that as a child, they were interested in sports, local plants and\nmushrooms, and pro wrestling. They were considered “tomboyish,” and were\nsocially ostracized from their peers because they were awkward and rude, and\nrefused to behave in “ladylike” ways. Even when Bobbi tried to conform to\ngender norms, they failed spectacularly. They lacked the fine motor control to\ndo makeup or write in pretty cursive letters. When girls subtly bullied them\nin the lunchroom for their short, self-chopped haircut, Bobbi couldn’t\nunderstand what was happening. They assumed that when girls yelled, “Hey\nBobbi, nice haircut,” they were being sincere.\n\nNo one flagged Bobbi as potentially Autistic, and they certainly didn’t\nrecognize Bobbi as potentially transgender, either.\n\n“I was just in this category of ‘weird annoying kid’ off to the side,” they\ntell me.\n\nIn both respects, it was easy for adults to write off Bobbi’s struggles as a\nmere annoyance, rather than a sign Bobbi was marginalized both in terms of\ngender and disability status. Masked Autism and being a closeted gender\nminority often go hand in hand, and the experiences share a lot of features.\nThe baffled families of transgender people and adult Autistics alike tend to\nclaim there “were no signs” of these identities when the person was\nyoung.[[1]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8314 \"note\") In\nactuality, there were often many signs, which the child’s family either did\nnot know to look for, or didn’t wish to\nsee.[[2]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8325 \"note\") Signs of\nnonconformity were likely met with admonishment, “helpful” condescending\ncorrections (“you look so unhappy, please smile!”), or by freezing the child\nout until they conformed. Bobbi was sarcastically complimented quite often,\nnot just for their hair, but for how they carried themselves, spoke, thought,\nand for the comfortable, practical ways that they dressed. As they grew older,\nthey began to figure out what was expected of them, and shifted their gender\npresentation to be more feminine so they could be seen as fully human.\n\nNo one in young Bobbi’s life could see them as they truly were. When your\nbelief system teaches that disability and gender variance are embarrassing and\ndisgusting, it’s hard to look at your child and recognize those traits. It\ncertainly didn’t help that in movies and television programs in the 1980s and\n1990s, Autistic people were all silent, passive nonentities, and transgender\npeople were perverted serial killers or trashy daytime TV curiosities.\n\nThese days, Bobbi surrounds themselves with fellow Autistic and transgender\npeople. They first discovered their disability after their eldest son was\nassessed in elementary school, and in the couple of years since then they’ve\ntried to build relationships that help them feel normal and seen for the first\ntime. They described their friend group to me as a land of misfit toys.\nThey’re all people who’d been shut out of mainstream society, most of them in\nmultiple ways. Even the public conversation about Autism ignores their\nexistence much of the time.\n\n“We have to make society over again from the ground up,” they say. “Our own\nlittle neuro-queer microsocieties. Because no one else will think to include\nus.”\n\nIn this chapter, I’d like to introduce you to the groups of people who most\ncommonly become masked Autistics. These are the people who have been\nsystematically denied access to diagnosis for decades, and are frequently\nstill ignored in public and psychiatric conversations about neurodivergence.\nThey’re Autistic women like Crystal, Autistic trans people like Bobbi, and\nBlack genderqueer people like Anand Prahlad. Some had their neurodivergence\nerased because they grew up in poverty, or because they had physical ailments\nthat obscured their Autistic traits. Some are assumed to be too “high\nfunctioning” to need accommodations, but actually suffer deeply from a lack of\naccessibility and support. Others are pretty clearly debilitated by disability\nbut were misdiagnosed as Borderline or Narcissistic instead of Autistic. In\ntheir stories, you’ll see just how multifaceted the Autistic community is, and\nhow painfully limiting stereotypes about the disability really are to each of\nus. You may also see yourself reflected in these stories or recognize someone\nyou know. The more Autism is understood and embraced in its full, rich\ndiversity, the less need there will be for these multiply marginalized\nAutistic people to keep themselves hidden behind a mask of quiet conformity.\n\n# Autistic Women and Gender Minorities\n\nMost of the writing and research about gender-based disparities in Autism\nfocuses on the fact that girls are woefully underdiagnosed. Researchers,\ntherapists, and even some Autistic self-advocates talk about “female\nAutism,”[[3]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8333 \"note\")\npointing to the fact that among girls, Autistic qualities do seem less severe\nor obvious on average.\n\nWhen Autistic girls engage in self-stimulatory behavior, it tends to be less\nphysically damaging: less arm biting, more hair twirling or opening and\nclosing a book quietly many\ntimes.[[4]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8344 \"note\") When\nAutistic girls are shy and withdrawn, people are less concerned by it than\nthey would be if a boy exhibited the same reticence. On the flip side, when\nAutistic girls have meltdowns, it tends to get written off as an emotional\noutburst. When they _do_ act out or behave aggressively, they’re more likely\nto be punished severely for not being ladylike, resulting in them learning to\ncensor their aggression at an earlier age than most boys\ndo.[[5]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8352 \"note\") Adults speak\nto young girls using more emotion-related words than they do when speaking to\nboys,[[6]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8366 \"note\") which\nmeans Autistic girls often get a leg up in social and relational skills. Much\nof the play that girls stereotypically engage in (and are encouraged to engage\nin) involves mimicking adult social interactions, such as playing house or\npretending to run a\nstore.[[7]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8377 \"note\") As a\nresult many Autistic girls learn how to fake their way through routine\nconversations at a younger age than boys do.\n\nFor these and a variety of other reasons, Autistic girls are assessed and\ndiagnosed at older ages.[[8]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8388\n\"note\") Many are diagnosed as adults, or are never diagnosed at all. Like\nCrystal, many Autistic women develop an inoffensive, quiet personality as a\ncrutch to counterbalance their social disadvantages. Unfortunately, adopting a\ndocile persona makes it even harder for their suffering to be seen as a real\nproblem.\n\nBelow is a table summarizing some of the most well-known “female Autism”\ntraits. It’s adapted from a list originally published on the now-defunct site\nHelp4Asperger’s, which was maintained by the author of the book _Aspergirls_ ,\nRudy Simone.[[9]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8396 \"note\")\nThis is by no means an exhaustive list, and shouldn’t be taken as a diagnostic\ntool. As I’ve already mentioned, the idea that all women have “female Autism”\nis a reductive one. Still, clinicians often fall back on tables like these to\ndetermine if an adult woman might potentially be an undiagnosed Autistic, so\nit’s something to be cognizant of. If someone is aware that a phenomenon such\nas “female Autism” exists, they’re often taught it looks something like this:\n\n# Traits Commonly Associated with “Female\nAutism”[[10]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8404 \"note\")  \n  \n---  \n  \n## Emotional\n\n  * Strikes others as emotionally immature and sensitive.\n  * Prone to outbursts or crying jags, sometimes over seemingly small things.\n  * Has trouble recognizing or naming one’s feelings.\n  * Ignores or suppresses emotions until they “bubble up” and explode.\n  * May become disturbed or overwhelmed when others are upset, but uncertain how to respond or support them.\n  * Goes “blank” and seems to shut down after prolonged socializing or when overstimulated.\n\n## Psychological\n\n  * Reports a high degree of anxiety, especially social anxiety.\n  * Is perceived by others as moody and prone to bouts of depression.\n  * May have been diagnosed with mood disorders such as Bipolar Disorder, or personality disorders such as Borderline or Narcissistic Personality Disorder, before Autism was discovered.\n  * Fears rejection intensely and tries to manage how other people feel to avoid it.\n  * Has an unstable sense of self, perhaps highly dependent on the opinions of others.\n\n## Behavioral\n\n  * Uses control to manage stress: follows intense self-imposed rules, despite having an otherwise unconventional personality.\n  * Is usually happiest at home or in a familiar, predictable environment.\n  * Seems youthful for their age, in looks, dress, behavior, or interests.\n  * Prone to excessive exercise, calorie restriction, or other eating disordered behaviors.\n  * Neglects physical health until it becomes impossible to ignore.\n  * Self-soothes by constantly fidgeting, listening to repetitive music, twirling hair, picking at skin or cuticles, etc.\n\n## Social\n\n  * Is a social chameleon; adopts the mannerisms and interests of the groups they’re in.\n  * May be highly self-educated but will have struggled with social aspects of college or their career.\n  * Can be very shy or mute, yet can become very outspoken when discussing a subject they are passionate about.\n  * Struggles to know when to speak when in large groups or at parties.\n  * Does not initiate conversations but can appear outgoing and comfortable when approached.\n  * Can socialize, but primarily in shallow, superficial ways that may seem like a performance. Struggles to form deeper friendships.\n  * Has trouble disappointing or disagreeing with someone during a real-time conversation.\n\n  \n  \nIn this list of traits, I do recognize elements of myself and many adult-\ndiagnosed Autistics I know of all genders. There’s a particular way the\nneurotype tends to present among people who only discovered the identity late\nin life. We tend to be emotionally withdrawn yet friendly and socially\nadaptive. We’re social chameleons, and masters at making people like us, but\nwe never let much of our real selves show. We erect rigid rules around our\nlives to manage stress and make an unpredictable social world feel a little\nless scary: _make eye contact for this many seconds, eat this easy-to-prepare\nmeal at this time of day, never talk about yourself for too long_. Try as we\nmight to be agreeable, people still comment on how “oversensitive” or\n“immature” we are, or imply we’re hard to read. When we struggle, people talk\ndown to us, or try to socially “mother” us into more normative behavior.\n\nLists like these are still pretty popular among\ntherapists[[11]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8415 \"note\") and\nin online spaces for Autistic people and our\nfamilies.[[12]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8424 \"note\")\nSometimes therapists who are seeking to educate themselves on “female Autism”\nwill encounter this list online and let it inform their views, or pass it\nalong to their patients. It offers a very broad, very gendered list of traits\nthat reflect a lot of cultural biases and assumptions. What does it mean, for\nexample, to “seem youthful”? Would a large, hairy man who loves collecting\nFunkopop toys but also enjoys MMA fighting be considered youthful? Or would\nthat label instead apply to a petite woman who wears dresses and speaks in a\nhigh-pitched voice about her love of horses? All too often, the difference\nbetween who gets perceived as an innocent, shy Autistic and who gets viewed as\ncreepy, awkward, and obviously disabled is more a function of things like\nrace, gender, and body size than it is any innate difference in personality or\nbehavior. There is no objective definition of what makes someone moody or a\nsocial chameleon, either. It’s easier to socially camouflage if you’re the\nkind of person society doesn’t view with much suspicion in the first place.\n\nThis cluster of traits is commonly called “female Autism,” but that label\nignores the fact that a large percentage of Autistic people are transgender\nand gender\nnonconforming.[[13]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8432 \"note\")\nI’m transgender and Autistic, and find that my experiences don’t fully slide\ninto either the “female” or “male” Autism narratives. I’ve always had some\nmale Autistic traits, like a tendency to be didactic and speak in a confident\nmonotone, yet I was also a “sensitive,” “immature” kid who played imaginary\ngames with toys into my teens. Calling any of these qualities signs of “male\nAutism” versus “female Autism” is as gender reductive as saying there’s an\ninnately “masculine” or “feminine” personality type.\n\nLike Bobbi, I was raised and socialized as a bit of an odd freak more than I\nwas a “boy” or a “girl.” Neither girls nor boys related to me as one of their\nown, and I didn’t identify with them, either. I felt more like a mystical\nfairy creature dropped into the wrong reality than I felt like a “female,” or\neven a human being. I played Legend of Zelda: Ocarina of Time and recognized\nmyself for the first time in the game’s wordless, androgynous protagonist\nLink. He didn’t speak, and didn’t belong in the community of childlike elves\nhe’d been raised in. His difference was what marked him as special and\ndestined to save the world. Link was brave, strong, and softly pretty, all at\nthe same time. He was clueless and ineffectual in most social situations, but\nthat didn’t keep him from doing important things or from being met with\ngratitude and affection everywhere he went. I loved absolutely everything\nabout Link, and modeled my own style after him for many years. I wore tunic-\nstyle dresses and kept my hair long and blond, which read as “feminine” enough\nto other people that they rewarded me for correctly playing the role of an\nattractive girl. But in actuality, it was a sneaky way to cosplay as my\nfavorite male video game character every day without consequence. On family\ncamping trips that were uncomfortably bug-ridden, hot, and socially\noverwhelming, I wandered the woods, pretending I was Link on an adventure\nacross Hyrule. I desperately needed a model of how to be comfortable in my own\nskin, and Link was there when nothing else was available.\n\nThis is actually a really common Autistic experience. Perhaps because so many\nof us are alienated from mainstream neurotypical life, we come to identify\nwith fantasy creatures,[[14]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8441\n\"note\") aliens, robots,[[15]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8449\n\"note\") or animals instead of the people around\nus.[[16]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8463 \"note\") Our\nhyperliteral, analytic minds recognize that the rules of the gender binary are\narbitrary and entirely made\nup,[[17]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8471 \"note\") so making\nup our own gender identities and rules of presentation seems like fair game.\nIdentifying outside of the binary (and outside of humanity) also helps many of\nus put a name to how detached we feel from society, and from our bodies. _Of\ncourse it’s hard for me to carry myself in a “ladylike” way, I’m a robot in a\nhuman suit!_ There’s a term for Autistic trans people who see their neurotype\nand gender identity as inextricably linked:\n_autigender_.[[18]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8482 \"note\")\n\nI asked Bobbi if they see their Autism and transness as being associated, and\nthey tell me, “Absolutely, yes, you can’t have one part of me without having\nthe other. My Autism is trans and my transness is Autistic. Bras were\nuncomfortable for gender reasons and because I can’t deal with tight clothes.\nI did soccer and flag football to be ‘one of the guys,’ and because when I was\nrunning around, nobody could talk to me or ask me questions that were social\ntraps. It’s all wrapped up together.”\n\nI feel the exact same way as Bobbi. I love that my Autism and my transness are\nlinked. On good days, I love being Autistic and see it as a natural, neutral\npart of my identity, so it never has struck me as a problem that it’s shaped\nmy gender. I’m not a “normal” person, have never been able to be one, so\nidentifying outside of the gender binary as well as mainstream humanity feels\nlike home.\n\nSadly, many “gender critical” parents and mental health professionals don’t\nsee it that way. Transphobic people often take the strong association between\ngender variance and Autism as a sign that we aren’t “really” trans, we’re\n“just” Autistic and\nconfused.[[19]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8490 \"note\") They\npresume Autistic people are un-self-aware and easily manipulated, and\ntherefore shouldn’t be allowed to make decisions about our identities or what\nwe do with our bodies.[[20]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8501\n\"note\") When Harry Potter author J. K. Rowling published the piece “TERF\n(trans exclusionary radical feminist) Wars” on her blog in the summer of 2020,\nshe specifically mentioned her fear that many transgender men are actually\nAutistic girls who weren’t conventionally feminine, and have been influenced\nby transactivists on the internet into identifying out of\nwomanhood.[[21]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8506 \"note\") In\npresenting herself as defending disabled “girls,” she argued for restricting\nyoung trans Autistic people’s ability to self-identify, and access necessary\nservices and health care.\n\nRowling’s perspective (which she shares with many gender critical folks) is\ndeeply dehumanizing to both the trans and Autistic communities. We’re fully\nfledged, complex people, who are entitled to the same body autonomy and self-\ndetermination as anyone else. And it’s meaningless to question whether a trans\nAutistic person would have “still” been trans had they not been born\nneurodiverse, because Autism is such a core part of who we are. Without our\ndisability (or our gender identity) we’d be entirely different people. There\nis no separating these aspects of ourselves from our personhood or\npersonality. They’re both core parts.\n\nLaura Kate Dale is a transgender woman, video game critic, and author who has\nwritten extensively about how her neurotype and gender have run parallel\nthroughout her life. In her memoir, _Uncomfortable Labels: My Life as a Gay\nAutistic Trans Woman_ , she writes that though she was viewed as a boy when\nshe was growing up, she didn’t have the traditional “cis boy with Autism”\nexperience.[[22]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8514 \"note\") She\nhad many recognizably Autistic traits, such as an aversion to bright colors\nand strong flavors, and a detachment from physical reality that made it\nimpossible to figure out what clothes to wear for any given day’s weather. Yet\nwhen she was evaluated for a variety of disabilities as a kid, counselors\ndidn’t consider Autism. Society had deemed her a “boy,” and “boys” with Autism\nweren’t supposed to be so docile and sweet. She had many of the features of\n“female Autism,” though the world did not yet recognize her as a female.\n\nLaura writes, “You see, there are stereotypes about children assigned male at\nbirth, and very few of them applied to me growing up. There’s an expectation\nof brashness, over excitability, loudness and emotional closure…. I was a\nquiet, reserved child who was sweet and did what they were told and was always\nin the right place, at the right time, doing what was\nexpected.”[[23]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8523 \"note\")\n\nLaura’s interests were often very feminine, rather than boyish. Like Crystal,\nshe didn’t disturb class with meltdowns or hurt anybody’s feelings by being\nblunt or rude. Since her internal suffering didn’t pose any problems to her\nclassmates or teachers, it flew under the radar, unremarked upon—which is\nexactly what happens to many cisgender Autistic girls. Even some of her\nAutistic traits got chalked up to her being a weird or effeminate kid, rather\nthan a disabled one.\n\nLaura’s and Bobbi’s experiences are perfect examples of why the term “female\nAutism” is misleading; it presents the root of masking as being a person’s\nassigned sex at birth, or their identity, when really it’s social expectations\nthat lead to a person’s disability getting ignored. Masking is a social\nexperience, not a biological one. “Female Autism” isn’t actually a subtype of\nthe disorder; it’s a way that people cope with their neurodiversity not being\ntaken seriously. Often, it is women who are in that position. But many other\nmarginalized groups go through it, too, and those trends have not been as\nwidely recognized. Black and brown Autistics in particular are underdiagnosed\nat high rates, just as women are, because racism has similarly distorted how\nthe disorder gets perceived and assessed. They also pay a huge price for being\nnonconforming and noncompliant, and are thus expected to mask as a means of\nsurvival.\n\n# Black and Brown Autistics\n\nRacism has permeated psychology and psychiatry from its genesis. Early\nclinicians came from white, European backgrounds, and used their culture’s\nsocial norms as the basis for what being healthy looked\nlike.[[24]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8531 \"note\") It was a\nvery narrow and oppressive definition, which assumed that being genteel, well\ndressed, well-read, and white were the marks of humanity, and that anyone who\ndeviated from that standard was not a person, but an animal in need of being\ntamed.[[25]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8539 \"note\")\n\nThe modern concept of mental illness as a medical condition first formed\nduring the Victorian period in England, a time and place where restraint and\ndignity was equated with\nsanity.[[26]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8547 \"note\") Even\npoor English people who couldn’t maintain the polished appearance and icy\netiquette of the wealthy were considered to be somewhat savage and sick.\nCultures that were more emotionally expressive or less filtered were\npathologized as irrational, oversexualized, and aggressive. The mental health\nneeds of white, wealthy people (and the hassle rich mentally ill people\npresented to their high-status families) were the primary concern of early\npsychiatrists. Everyone else was, at best, an afterthought, and at worse an\nundesirable to be purged.\n\nThis history shaped how professionals saw and defined Autism from the very\nstart, and its legacy is still with us today. Autistic people of color\nfrequently end up having their Autism ignored due to racism and\nbigotry.[[27]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8555 \"note\")\nThey’re less likely to get referrals to Autism\nspecialists.[[28]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8566 \"note\")\nThey have an incredibly hard time finding culturally competent health\ncare.[[29]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8577 \"note\") Only\nabout 4 percent of all mental health providers in the United States are\nBlack,[[30]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8588 \"note\") though\nBlack people make up 13.4 percent of the country’s overall population. When\nBlack and brown Autistic people see white therapists, normal expressions of\nemotions like anger may be misperceived as excessive or “threatening,” and\nmisdiagnoses are very\ncommon.[[31]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8597 \"note\") That’s\nif they get identified as having a mental health condition at all. Black\nAutistics are frequently obligated to mask their traits and any negative\nmental health symptoms because (like girls and gender minorities) society\ndemands they be more obedient and agreeable than white boys are.\n\nComedian Chris Rock recently came out about being on the Autism spectrum;\nspecifically, he was diagnosed with Nonverbal Learning Disorder. In an\ninterview with _The Hollywood Reporter_ , he describes how clear-cut\nindicators (such as an inability to pick up on social cues and a tendency to\ntake all statements hyperliterally) were ignored until his mid-fifties.\nBecause he was an outgoing, Black comedian, Autism seemed unthinkable as an\nexplanation for the social and emotional challenges he was\nfacing.[[32]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8605 \"note\") Rock\nsays he downplayed his own mental health needs, too, because he’d internalized\nthe idea only white people go to therapy.\n\nThis is a systemic and far-reaching problem. White Autistics are 19 percent\nmore likely to be diagnosed than Black Autistics are, and 65 percent more\nlikely to be diagnosed than Latinx\nAutistics.[[33]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8613 \"note\")\nBlack and Latinx Autistic people also get their diagnoses at older ages,\nreflecting their delayed access to\nservices.[[34]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8622 \"note\")\nIndigenous Autistics are underdiagnosed and delayed in their diagnoses at even\nmore extreme rates.[[35]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8633\n\"note\")\n\nThese long-standing racial and cultural gaps persist for a variety of reasons.\nThe lower a family’s socioeconomic status, the less likely they are to have\naccess to health care of any kind, but particularly Autism testing, which is\nseldom covered by insurance and can cost thousands of dollars. Additionally,\nracism influences how teachers and specialists perceive and screen for\nAutistic traits in Black and brown kids. When a white kid doesn’t listen to\ninstructions and hurls blocks across the room, he might be gently chastised,\nor soothed. When a Black or brown kid does the exact same thing, he’s\n“corrected” far more aggressively. He might even be treated as a future\ncriminal in the making.[[36]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8644\n\"note\")\n\nThe writer Catina Burkett is a Black Autistic woman, and she is acutely aware\nof how people’s perceptions of her disability are mediated by _misogynoir_ ,\nthe systemic oppression of Black\nwomen.[[37]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8658 \"note\")\n\n“Many people with autism can also appear obstinate or are slow to react in new\nsituations,” Catina writes. “When I am inflexible, I am sometimes called\nunfriendly, insubordinate, lazy, aggressive or uncontrollable.”\n\nI’ve known quite a few white Autistic men who are, as Catina puts it,\nobstinate at work. If the white guy in question has an advanced degree or a\ndesirable skill set, such as the ability to code, being a bit difficult to\ndeal with doesn’t necessarily get in his way. In fact, for some Autistic men\nin tech, being a bit arrogant or cold can work to their advantage. Their\naloofness signals they must be a tortured genius, a Sherlock in an office of\nWatsons. Yet when a Black Autistic woman is even slightly flat in her\nemotional expressions, she has to worry people will call her “angry” or\n“unprofessional.”\n\n“One white female supervisor complained that I should learn to change my\ndemeanor with different people,” writes Catina. “[She] grew bitter and the\nwork environment became hostile. Eventually, I had to quit.”\n\nCatina’s boss was, in essence, asking her to _code switch_ , and put on\ndifferent linguistic and social presentations for different situations. Many\nBlack Americans are conversant in code switching, having to shift between\nAfrican-American English (or\nAAE)[[38]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8666 \"note\") and\nStandard English as they move between communities, and modulating their\nappearance, mannerisms, and volume to avoid being negatively\nstereotyped.[[39]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8674 \"note\")\nCode switching is similar to Autism masking in the sense that it’s an\neffortful process of signaling you “belong” in a space, and of knowing when to\nhide the sides of yourself that the majority will be oppressive toward. Code\nswitching is a cognitively demanding activity that can hinder a person’s\nperformance on challenging or demanding\ntasks,[[40]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8685 \"note\") and it\nis associated with psychological stress and feeling inauthentic and socially\nisolated.[[41]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8696 \"note\") A\nreport in _Harvard Business Review_ found that many Black code switchers\ndescribed it as a state of hypervigilance, and that they needed to constantly\npolice their actions and speech in order to minimize white discomfort or\nhostility.[[42]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8707 \"note\")\n\nBlack Autistic people can have a variety of complicated relationships to\nmasking and code switching. Pretending to be neurotypical by one culture’s\nrules is wearying enough. Having to do it in a variety of different ways,\nusing different dialects and mannerisms depending on the setting, is an\nentirely different level of social performance. Autistic researcher and\norganizer Timotheus Gordon Jr. told me that learning to code switch in his\nspeaking style actually led to him becoming more socially ostracized as an\nAutistic child, not less.\n\n“Because I’m African American, I have a different English to speak,” he says,\n“which is African-American English. So I was placed into speech therapy, in my\nopinion, to sound like a person who speaks the standard American English.”\n\nIn speech therapy, Timotheus was trained to communicate more like a white,\nmiddle-class person would; in essence, he was being told to mask his culture.\nBut since he went to a majority Black school, this didn’t help him fit in, it\nmarked him as different.\n\n“I went to school with mostly African Americans, or folks of African descent.\nIt backfired because I was mocked for speaking differently, or speaking like\nI’m from England.”\n\nOver time, Timotheus had to learn to mask his speaking style in order to fit\nin with his peers, but also to shift back into so-called standard American\nEnglish when interacting with white people and institutions. Psychological\nresearch shows that code switching requires a ton of cognitive resources even\nfor neurotypical\npeople.[[43]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8715 \"note\") One\nmasked Autistic woman I spoke to, Mariah, told me that for many years she\nthought code switching exhausted her. Eventually, though, she discovered that\nit was the masking as neurotypical that was wearing her out. For some Black\nAutistics like Catina, it can be prohibitively hard to manage both tasks.\nSince she couldn’t will herself to transform into a cheery, enthusiastic\npersonality at will, her boss viewed her as hard to work with.\n\nFor Autistic people of color, being seen as hostile or difficult can become\ndownright dangerous. When Black and brown Autistics fail to comply with\nmedical instructions or the directions of therapists, they’re frequently\ninstitutionalized and stripped of legal\nautonomy.[[44]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8726 \"note\") They\nalso have to worry about incarceration or death at the hands of police. In\n2017, Chicago police sergeant Khalil Muhammad shot an unarmed, Black Autistic\nteenager named Ricardo Hayes. Muhammad claimed he felt threatened by Hayes,\nbut an investigation revealed Hayes had been harmlessly jogging along the side\nof his street, and didn’t show any aggression toward\nMuhammad.[[45]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8735 \"note\") Five\ndays after the murder of George Floyd, an Israeli police officer in Jerusalem\nCity shot and killed Eyad Hallaq, an Autistic Palestinian man who was\nprofoundly intellectually disabled and unable to speak or comprehend\ninstructions.[[46]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8743 \"note\")\nIn April 2021, a Chicago police officer shot and killed thirteen-year-old Adam\nToledo, who had his hands in the air. Adam was in special education and\nneurodivergent.[[47]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8751 \"note\")\nApproximately 50 percent of people who are killed by police have\ndisabilities,[[48]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8760 \"note\")\nand Black and brown Autistics are at an especially elevated\nrisk.[[49]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8768 \"note\") Being\nidentified as Autistic can be socially and emotionally perilous for women and\ngender minorities, regardless of race; for Black and brown Autistics, being\nvisibly disabled can be deadly.\n\nIn _The Secret Life of a Black Aspie_ , folklorist Anand Prahlad illustrates\nin lush detail how it felt to mask his Autism and present a neurotypical,\nnonthreatening façade to the world:\n\n“I learned to grow masks for school. I had to be careful there. Covering up\nwas like an instinct, though. Like a brown walking stick turning green when it\nsits on a leaf. Watch…Watch hands. Watch lips. Watch\neyebrows.”[[50]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8776 \"note\")\n\nAnand grew up on a plantation in the 1950s, just two generations from the end\nof slavery. Living in a rural area with his family (many of whom had Autistic\ntraits), Anand found comfort in nature. Upon entering the school system,\nthough, he had to mask up. In addition to being Black and Autistic, Anand is\nalso genderqueer, so as soon as he was thrust into public school, he had to\nbegin hiding his neurodivergence as well as his soft, feminine side.\n\nThroughout the book, Anand describes how various social settings demanded\ndifferent versions of him. There was the all-Black elementary school where he\nwas seen as odd, and not sufficiently masculine, but mostly left alone; there\nwas the integrated high school where white people placed a great deal of\npressure on him to be a respectable vanguard for racial justice. As an adult,\nAnand became a professor. In the academy, he was required to hide all\nemotional vulnerability, censor all casual language and slang, and obscure\nanything else white colleagues would deem “unprofessional.” Autistic people\nare usually pretty candid, and Black American culture tends to also value\ndirect “real talk” about interpersonal\nissues.[[51]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8784 \"note\") But in\nmajority-white, abled institutions, openly saying what you mean or complaining\nabout anything scares people. Anand had to adapt to hide the parts of himself\nthat were open, vulnerable, and\nreal.[[52]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8792 \"note\")\n\nThroughout his memoir, Anand describes how erecting false selves was\nnecessary, but also made it impossible to genuinely connect with others. It’s\nan experience I know that many masked Autistics can relate to. We have to keep\nother people at arm’s length, because letting them see our hyperfixations,\nmeltdowns, obsessions, and outbursts could mean losing their respect. But\nlocking ourselves away means we can’t ever be fully loved.\n\n“I would never have survived following neurotypical rules,” Anand writes. “But\nmy rules weren’t necessarily the best ones to follow in a relationship. For\nexample, my rules said disconnect the minute I’m overwhelmed. Stop\nlistening…Keep my secrets.”\n\nAnand went through several breakups and multiple divorces before finally\ngetting diagnosed as Autistic. Instead of sharing his feelings with his\npartners, he’d run away, either physically or into the recesses of his mind.\nWhen his third wife suggested this might be caused by a disability, Anand\nfinally was put on a path toward self-acceptance.\n\nMasking is a sensible survival strategy when you have no other tools at your\ndisposal. But the more you deviate from what society values, the more\nelaborate your masking must be. Hiding your Autism, your cultural Blackness,\n_and_ your queerness or womanhood can be too much. Sometimes the only viable\nalternative is to shut down and become deeply inhibited. You can’t offend\nanyone if you simply melt into the wallpaper.\n\nCatina Burkett and Anand Prahlad both describe adopting this strategy,\nbecoming quiet and repressed, keeping their heads down to avoid evoking white\npeople’s fear of confident Black personhood. Other Black Autistics get by in\nlife the way Chris Rock has, working to come across as cheery, funny, and\nimmensely likable. Just as many Autistic women and trans people adapt by\nbecoming nonthreatening and small, Black Autistics frequently have to self-\npreserve by plastering on a smile.\n\n# Highly Verbal and Outgoing Autistics\n\nIn 1911, the psychiatrist Eugene Bleuler coined the term\n_autism_.[[53]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8803 \"note\") It\nliterally means “isolated self.” This is in contrast to the term for non-\nAutistic, _allistic_ , which means other-self or connected-\nself.[[54]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8811 \"note\") Countless\ndepictions of Autism on TV and in film focus on how alienated and in our own\nheads we supposedly are. Think of the Autistic boy in the series finale of\n_St. Elsewhere_ , who is famously revealed to have dreamed up the entire show\nand all its characters while sitting off by himself, staring into a snow\nglobe.[[55]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8816 \"note\") A more\ncontemporary example is the titular character in Sia’s widely\npanned[[56]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8825 \"note\") film\n_Music_ , a nonverbal Autistic girl who barely seems to notice when her own\ngrandmother dies right in front of her. In the film, Music can’t speak, and\ncan barely use the augmented communication device she’s been given, and only\nconnects with other characters through elaborately choreographed dream\nsequences.[[57]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8836 \"note\")\nShe’s an isolated, antisocial self, locked away in a world of her own making.\n\nThough a majority of diagnosed Autistics report having introverted personality\ntraits,[[58]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8844 \"note\") some of\nus are actually quite extroverted and\noutgoing.[[59]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8855 \"note\")\nExperimental research suggests that some of the social skills deficits\nassociated with Autism (for example, difficulty recognizing faces) are reduced\namong Autistics who are\nextroverted.[[60]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8866 \"note\") If\nyou seek out a lot of social contact, you’ll get more practice interacting\nwith people, so it makes sense that extroverted Autistics gradually learn to\nmore easily blend in. Extroverted Autistics also tend to have larger, more\nexpressive emotions than their introverted peers, which can make them easier\nfor neurotypicals to relate to.\n\nAutistics can have intense and bright personalities just as easily as we can\nseem icy and withdrawn. Many can make strong eye contact, listen actively, and\njump in excitedly when someone brings up a topic that interests us. Outgoing\nAutistics may fumble with social niceties, interrupt too often, seem “too\nenthusiastic,” or even be accused of histrionics, but a high degree of\ninterest in connecting with others does generally benefit them psychologically\nand socially.[[61]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8877 \"note\")\n\nUnfortunately, because Autism is so singularly portrayed as a disorder that\nmakes you cold and robotic, outgoing Autistics are seldom correctly identified\nand diagnosed as kids. Teachers and parents think of them as chatty social\nbutterflies, or disruptive class clowns. People may even come to view their\nlarge emotional displays and bursts of energy as “manipulative” or “attention\nseeking.” Over time these labels can become a part of the mask they wear to\nget by. It can also make it difficult for an Autistic person to have their\nneed for alone time or other social boundaries respected. For example,\nTimotheus told me that since he can come across as an affable “life of the\nparty” type, it can be hard for his friends and family to understand that he\nsometimes also needs to recharge alone.\n\n“My grandparents originally came from the deep South, so in that cultural\nsense it was important nobody gets left out,” he explains. “If you feel sad,\nthen it’s best to be in a group. But in my case, I need to be left alone. But\nif I say to peers or even family members, _I need my alone time_ , they say\n_no no no, you can’t be alone_. I’m damned if I do, damned if I don’t.”\n\nIn many different ways, masking as outgoing and sociable can lead to an\nAutistic person’s struggles being underestimated or erased. My friend Bethy is\nenergetic, wears lots of eye-catching, bright clothing, and is covered in some\nof the coolest tattoos I’ve ever seen. They’ve been active in Chicago’s\ntheater and circus arts communities for years, and when they’re excited, they\njump and down squealing with delight. Bethy also loves modeling, and is very\nin tune with their body and sensuality. They treat their personal style and\nphysicality as a full extension of their selfhood. For many, these qualities\nwould be a bit surprising to witness in an Autistic person. So many of us have\npoor coordination and feel at odds with our\nbodies,[[62]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8888 \"note\") and\nwe’re stereotyped as uncool nerds with no sense of style. Bethy is pretty\nvisibly Autistic, but they’re also very charming. If I didn’t know better, I’d\nassume their sunny, graceful personality meant they had an easier time\nsocializing than more withdrawn, shy Autistic people do.\n\nBut because I know Bethy well, I realize none of that is true. While they\nfound it easy to make surface-level friends at the bar where they use to work,\nthey say that bonding with someone in a deeper way proved very difficult. They\nsecond-guess themselves, and are constantly running an algorithm in the back\nof their mind about how their actions and words will be received by others.\nThey think a lot about how they’re perceived and rarely feel at home in any\ncommunity. Their immaculate style is also an effort to have their personhood\nand individuality recognized by other people. They’ve always been\nmisunderstood, and every day is a fight to communicate who they really are.\nBethy is masking, and putting extensive energy into doing so—just like\ninhibited, quiet me.\n\nJust as some Autistics desire a lot of social contact, some seek out a high\ndegree of stimulation and sensory input. Contrary to popular belief, Autism\ndoesn’t make a person’s hearing super sensitive or their eyes super responsive\nto light. What Autism actually does is influence how our brains filter through\nthe information taken in by our senses, and how we combine all that data into\na cohesive whole. That can manifest in us being either _sensory seekers_\n(sometimes called sensory inattentive\ntypes)[[63]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8899 \"note\") or\n_sensory avoiders—_ and most of us are a combination of both, depending on the\nsense.\n\nFor various reasons I outlined in Chapter 1, neurotypical brains tend to\ndismiss small details that might detract from the “big picture” their brain\nbelieves it sees.[[64]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8910\n\"note\") Metaphorically, when a neurotypical person sees a “forest,” their\nminds start glossing over the dead, bare trees and clumps of hedges that\ncomplicate the view.[[65]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8925\n\"note\") In contrast, Autistic people perceive all the individual trees, and\nstumps, and rotting animal carcasses. The thousands of small features don’t\neffortlessly combine into something larger for\nus,[[66]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8936 \"note\") so we have\nto process all of it separately. It’s exhausting.\n\nWhen I walk into my apartment building at night, I’m hit with a wave of\ndiscordant sensory information. It’s particularly bothersome if I’ve already\nhad a stressful or emotionally taxing day and my energy is depleted. There’s\nthe frenetic chatter of my neighbors, and the chaotic slamming of doors all\nalong the hall. I can hear the elevator groaning to the ground level, my\nneighbor’s music thudding below me, and ambulances blaring in the distance.\nEach piece of sensory information vies for attention, and doesn’t blend into\nuniform background noise. In fact, the longer I have to endure it, the more\nannoyed I become. One way I can cope with this is by blocking out the world\nand dampening all the stimuli that are distracting me. But another, equally\neffective way to cope with sensory challenges is by seeking out really strong,\nbold sensations that overpower all that white noise.\n\nWhen an Autistic person is a sensory seeker, they might crave loud music,\nspicy food, blazing bright colors, or plenty of activity and motion. They\ndon’t wear headphones in public to drown out the overwhelming noise of other\npeople, but because a thumping synthpop track helps keep them engaged and\ngrounded. The goal is the same in either case—to make sense of a barrage of\ndata that’s hard to process. A sensory seeking, fun-loving persona makes for a\nvery effective Autism mask; no one sees you as an “overly sensitive” disabled\nperson if you’re constantly traveling the world and thrashing to the music at\nyour local bar’s metal night. It might even be an enjoyable mask to wear,\nthough needing to constantly seek out stimulation can prove limiting. In their\nessay “Autistic People Party, Too,” the writer Jesse Meadows describes how a\ndrinking, drugging party-girl persona helped them fit in with other people and\nfind a modicum of sensory\ncomfort.[[67]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8948 \"note\")\nEventually, though, that lifestyle proved unsustainable, and they had to learn\nto seek novelty and stimulation in healthier ways.\n\nLogan Joiner is a teenager who has been sharing his passion for roller\ncoasters with the world since he was eight years old. On his two YouTube\nchannels (KoasterKids and Thrills United), he has a combined viewership of\nnearly thirty-five thousand subscribers. He shares videos of himself bungee-\njumping from bridges, cliff diving into open bodies of water, and racking up\namusement park visits. Logan’s Autistic, and he got into roller coasters\nbecause they help him regulate how his brain processes sensory information.\n\n“I’m not a big fan of unexpected surprises,” Logan has\nexplained.[[68]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8956 \"note\") “But\nif you think about it, roller coasters aren’t really like that…so they’re not\nscary because they’re predictable.”\n\nDespite how messy and noisy they can be, amusement parks can actually be quite\ncomforting to Autistic people. Amusement parks offer predictable social\ninteractions and prepackaged experiences that rarely change. The layout is\nclearly marked, the food is bland yet filling, every attraction is over in a\nmatter of minutes, and the signage is big and clear. Once you get used to a\nroller coaster, it provides consistent stimulation at expected points in time.\nFor sensory-seeking Autistics, the rushing wind and vibrations of the track\ncan provide relaxing physical input, just like a weighted blanket or fidget\ncube, only more forceful. There are statistics to memorize, development and\nlaunch history to learn about, and a whole community of nerdy online creators\nto share coaster and attraction lore with. Plus, on a roller coaster you can\nshout and flail your arms without anyone giving you funny looks. Since many of\nus have trouble regulating speaking volume and love to arm-flap, roller\ncoasters, concerts, and other noisy, raucous spaces can be unexpected refuges\nfrom social judgment.\n\nI have known Autistics who are DJs, salespeople, team managers, nonprofit\nfund-raisers, and aerialists. The more outgoing and sensory seeking among us\nlove anime conventions, house parties, political campaigning, and competitive\nsports. It’s often very difficult, though, for these kinds of Autistic people\nto get their disability taken seriously, because they can be so outspoken and\ncharming. When they do have trouble socializing or they fall behind at work,\ntheir loved ones accuse them of “faking” that they’re having a hard time,\nbecause they found it effortless to go out and party at a burlesque show the\nevening before. It’s an all-too-common experience for disabled people, being\ntold that your skills in one area are proof that you’re “not trying hard\nenough” in another.\n\nVery few people would guess these outspoken, high-energy folks are Autistic,\nparticularly during their rambunctious childhoods. If anything about them\nseemed unusual, ADHD was probably what people guessed. Incidentally, Autism\nand ADHD co-occur at very high rates, and are diagnostically quite difficult\nto untangle.[[69]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8964 \"note\")\nPsychologists often call them “sister conditions” because both of them impact\nthings like distractibility, sensory seeking, and being deeply pained by\nsocial rejection. This brings me to the next group of Autistics who often get\noverlooked: those with comorbid and overlapping conditions.\n\n# Autistics with Other Conditions\n\nWhen it comes to mental illness and disability, diagnostic categories are\nreally flawed things. A disorder is a cluster of symptoms and traits that tend\nto go together, but don’t always, and the way those clusters get organized\ntends to change over time. Psychologists have been debating for decades\nwhether anxiety and depression should be considered elements of the same\ndisorder, for example, or looked at as separate conditions that are just\ncorrelated.[[70]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8975 \"note\")\nPsychiatrists in the 1940s believed Autism was a form of childhood\nschizophrenia,[[71]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8989 \"note\")\nbut they certainly don’t see it that way now. Our understandings of these\nlabels are constantly in flux, and who gets stuck with a particular label\nvaries across time and cultural context.\n\nOften, a person exists somewhere on a spectrum between multiple disorders, or\nhas a unique combination of traits from multiple conditions. If you have ever\nhad a single manic period in your life, you may get diagnosed with Bipolar\nDisorder rather than Major Depressive Disorder, for instance, even if the\ndepressive episodes massively outnumber the manic ones. On the flip side, if\nyou don’t meet the low weight requirement for Anorexia, you may never get your\ndisorder recognized no matter how much anguish it presents in your life. This\ndynamic is particularly challenging for people with Autism Spectrum traits,\nbecause our neurotype is so multifaceted and so easily mistaken for other\nconditions.\n\nPeople with post-traumatic stress disorder, for example, can look very similar\nto Autistic people. PTSD sufferers tend to be afraid of large crowds, are\neasily rattled by loud noises, and become more reserved when placed in hard-\nto-read situations. PTSD-fueled hypervigilance can look a lot like masking:\nyou’re constantly scanning your environment for threats, and modulating how\nyou present yourself, so you can stay safe. To complicate matters, many\nAutistic people experience trauma at a young age, and have PTSD symptoms from\nthat. It’s common for us to be mistreated by parents and caregivers, bullied\nby classmates, or seen as “easy prey” by abusers. The leading treatment for\nAutism in children, Applied Behavioral Analysis therapy (or ABA for short),\nhas widely been criticized by Autistic people as being traumatic to endure.\n\nFor all these reasons, it’s not always possible (or helpful) to try to\nuntangle which of a person’s traits are Autistic and which are caused by the\ntrauma of being neurodiverse in a neurotypical world. Daan is a forty-year-old\nman living in the Netherlands, and in addition to being Autistic, he was\nabused by both his parents. He tells me his diagnosis of complex PTSD\neffectively masked his neurodivergence for many, many years.\n\n“I assume everybody is talking about me and is a hair’s breadth from blowing\nup and calling me a horrible person,” he says. “And is this Autism and not\nhaving a good theory of other people’s thinking? Or is it that my mother would\nhurl invectives at me if I so much as put the sponge on the wrong side of the\nsink? There is no answer.”\n\nDaan’s first trauma therapist tried to teach him that his fears were\nirrational; his mother was long dead, she told him, and could never hurt him\nagain. She believed that she could help him question the “illogical belief” he\nhad that people were unsafe. But Daan was still actively being hurt and\nrejected almost every day of his life because he was Autistic. His perceptions\nof the social world as menacing were realistic, not illogical.\n\n“I would make observations that were just, literal facts, like _oh hey you got\na haircut_ , and people would think I was making fun of them,” he tells me.\n“My boss screamed at me for that. Girls would go out with me and then berate\nme for not acting the way they expected a grown man to act. It was like my\nmother attacking me all over again. And then I would go to the therapist and\nshe’d say I was reliving my trauma with my mother and seeing her in other\npeople. It was horrible, crazy-making stuff really.”\n\nClinical studies show Daan’s experiences are far from abnormal. Therapy that\nis focused on battling “irrational beliefs,” such as cognitive behavioral\ntherapy (CBT), doesn’t work as well on Autistic people as it does on\nneurotypicals.[[72]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e8997 \"note\")\nOne reason for that is many of the fears and inhibitions of Autistic people\nare often entirely reasonable, and rooted in a lifetime of painful\nexperiences. We tend to be pretty rational people, and many of us are already\ninclined to analyze our thoughts and feelings very closely (sometimes\nexcessively so). Autistics don’t need cognitive behavioral training to help us\nnot be ruled by our emotions. In fact, most of us have been browbeaten into\nignoring our feelings too much.\n\nRecently, Daan switched therapists. His new therapist had only taken one\ncontinuing education course on Autistic adults in her entire career, but that\nstill made her better informed than most providers. She sent Daan to get\nassessed, and began to read up on how to alter her therapeutic practice to fit\nhim better.\n\n“My new therapist admits there isn’t much research on helping Autistic people\nwork through trauma,” he explains. “But she at least got me evaluated. And\nthat has unlocked a world of understanding for me, because it’s helped me talk\nto other Autistics online.”\n\nAutism can also look a lot like an anxiety disorder. Most of us are anxious\nnearly every moment we’re around other people, after all. Overstimulating,\nunpredictable surroundings will tend to activate our fight-or-flight response.\nThe rituals and repetitive behaviors we develop to cope with stress can look a\nlot like Obsessive-Compulsive Disorder. Autistic burnout presents very much\nlike a major depressive episode. All too often, these negative mental health\nconsequences of masking are what a therapist recognizes, rather than the\nuntreated disability that’s caused it.\n\nSome undiagnosed Autistic people (particularly women) identify as “highly\nsensitive persons.”[[73]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9008\n\"note\") Highly sensitive persons are generally described as intuitive,\nemotionally astute, and easily overwhelmed. Even the creator of the term,\nElaine N. Aron, has revealed that some of the highly sensitive family members\nshe has described in writing later found out they were\nAutistic.[[74]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9016 \"note\") The\nstigma that comes with Autism (and its very male, standoffish associations)\nmay be part of why so many women on the spectrum find labels such as _anxious_\nand _highly sensitive_ to be far more resonant.\n\nIn some cases, marginalized Autistic people get stuck with mental health\ndiagnoses that are even more reviled and misunderstood than Autism is. It’s\nquite common for adult Autistic women to be incorrectly labeled with\nBorderline Personality Disorder, for\ninstance.[[75]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9024 \"note\") This\nis a really disastrous diagnosis. Borderline Personality Disorder is many\ntherapists’ least favorite condition to work\nwith.[[76]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9032 \"note\") As a\ngroup, they’re commonly viewed as overly dramatic, needy, attention seeking,\nunreliable, and even\nabusive.[[77]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9043 \"note\") When\nI’ve taught psychotherapists in training, many of them have shared with me\nthat their supervisors taught them to avoid BPD sufferers like the plague, and\nto never even befriend a person with BPD traits.\n\nThough it’s called a disorder of “personality,” BPD could perhaps be more\ncorrectly described as a disorder of attachment and emotional\nprocessing.[[78]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9055 \"note\")\nPeople with BPD fear rejection very intensely. They have an unstable sense of\nself that’s highly dependent on the acceptance of others. They’re often\ndescribed by loved ones and therapists as having extreme emotions that seem\ninappropriate or\nmanipulative.[[79]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9069 \"note\")\nIf these sound eerily similar to the “female Autism traits” from the table\nearlier in this chapter, that’s not a coincidence. Many women (and other\ngender minorities) who have been repeatedly rejected and traumatized for being\nAutistic develop an insecure sense of self, a (reasonable) fear of rejection,\nand big “overly sensitive” emotions that reflect the distress they almost\nconstantly feel.\n\nNylah is one such woman who was incorrectly labeled as BPD before finally\narriving at an Autism diagnosis. She had all the traits that tend to overlap:\ninsecure self-esteem, fear of being abandoned that would prompt emotional\nmeltdowns, and an unstable sense of who she was.\n\n“I used to pretend to be whoever my boyfriends wanted me to be so they\nwouldn’t leave me. And that was supposedly so manipulative and evil of me,”\nshe says.\n\nIn actuality, Nylah was trying desperately to not be alone. If a partner was\ninto hockey, she filled her wardrobe with hockey jerseys. If a guy liked women\nwho dressed up, she started getting weekly manicures. It didn’t work great,\nbut it was all she knew.\n\n“Living so falsely made me feel suicidal, and what do you know, attempting\nsuicide when you have Borderline means you’re manipulating people for\nattention,” she says. “I was the one constantly setting myself up to be taken\nadvantage of, but with the Borderline target put on my back, I was a\nhysterical villain in people’s eyes.”\n\nNylah only began to question this narrative about herself when a relative\nreceived an Autism diagnosis. At age sixty-five, her mother got assessed—after\nmany decades of carrying an equally stigmatizing Narcissistic Personality\nDisorder diagnosis.\n\nNylah says, “My mother is very self-involved, but that’s because she literally\ncannot understand what’s happening in others’ brains and she can get so locked\ninto her own view. Her actions can seem selfish because Autism gets in the way\nof her empathy. I have really intense empathy, it is painful almost, and she\nis the flip side. She just doesn’t have it. But is that evil? She literally\ncannot help it.”\n\nNylah shares with me that though her mother is inconsiderate and stubborn, she\nis also a woman who cares deeply about the world. Anything that gets in the\nway of her activism is a threat to be excised from her life. Recognizing that\nabout her mom, and admiring that passionate, dedicated side of her has helped\nNylah feel more at peace about their relationship.\n\n“She cares very much about feminism and saving the environment. Her heart is\nbig and it is wounded. She’s a difficult person doing her very best, which in\na Black woman seeking therapy in the 1970s meant you were a narcissist,\napparently.”\n\nAn article by psychiatrists Meng-Chaun Lai and Simon Baron-Cohen, published in\nthe medical journal _The Lancet,_ has proposed that an entire generation of\nAutistic people were misdiagnosed as having personality\ndisorders.[[80]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9085 \"note\")\nUnsurprisingly, they propose that most of the misdiagnosed were marginalized\nwomen. Usually, I find a lot of problems with Baron-Cohen’s work; he has long\nbeen an advocate for the view that Autism is best understood as an “extremely\nmale brain.”[[81]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9093 \"note\")\nYet in this research, he seems to acknowledge that the reason many women are\nnot diagnosed as Autistic is because they’re labeled as Borderline,\nHistrionic, or Narcissistic instead. Getting stuck with a personality disorder\ndiagnosis also makes it very difficult for a patient to find affirming,\ncompassionate mental health care, particularly if that stigma interweaves with\nsexism or misogynoir.[[82]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9098\n\"note\")\n\nAs I briefly mentioned above, Autism and ADHD co-occur and overlap immensely.\nBoth disabilities relate to a person’s “executive functioning,” meaning their\nability to plan ahead, divide large goals into smaller steps, sequence tasks\nin a logical order, and self-motivate to complete them. Yet even the fact that\nwe struggle with these activities is contextual, and cultural: in a world\nwhere rugged individualism wasn’t prioritized, it might not be a disability to\nneed help finding your car keys. Both Autistics and ADHDers are easily\ndistracted by stimuli, yet also prone to hyperfixating on activities we find\nenjoyable, getting engrossed for hours without remembering to pee or eat.\nGenerally speaking, Autistics tend to perceive themselves as having more\ncontrol over what they hyperfocus on than ADHDers do. ADHDers are more likely\nto describe boredom and understimulation as _painful,_ where as some Autistics\nreally enjoy stillness and quiet. Both neurotypes are underdiagnosed in women\nand people of color, and those who aren’t diagnosed at a young age typically\nwind up masking for decades before figuring their identity\nout.[[83]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9109 \"note\")\n\nThough ADHD is not believed by professionals to affect emotional processing\nand social skills development directly, one prominent experience among ADHDers\nis _rejection-sensitive dysphoria_ , feeling intense panic and distress when\nreceiving negative (or even neutral) social feedback from other people.\nBecause ADHDers find rejection so terrifying and painful, their social\nbehavior can be just as restrained and people-pleasing as that of masked\nAutistics. Autistics may have trouble guessing what other people are feeling\nor understanding unspoken social norms, but ADHDers may also be accused of\nbeing “oblivious” too, talking at length without picking up on others’\nboredom, or getting so lost in a video game or favorite hobby that they miss\ntheir roommate frustratedly doing all the cleaning. The underlying mechanisms\nmight be different, in other words, but many of the struggles are the same.\n\nWhile ADHDers don’t appear to process information in as bottom-up a fashion as\nAutistics do, the high energy and anxiety associated with the neurotype can\nlook incredibly similar to how Autistics react to overwhelming sensory\ninformation.[[84]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9117 \"note\")\nAnd while some masked Autistics may generally be better at staying on task,\nmaintaining a consistent schedule, and keeping organized compared to the\naverage ADHD, many of us are so chronically exhausted and burnt out that we\nexperience the same struggles with daily life that people with ADHD do. Plus\nthere are plenty of non-masked Autistics who require daily assistance, so it’s\nnot fair to say that Autism is a more functional or organized\nneurotype—however, Autism is often stereotyped to be the “order” to ADHD’s\n“chaos.”\n\nThough we have many experiences in common, there are some differences between\nADHDers and Autistics worth noting. First, an ADHD diagnosis is easier to\nreceive as an adult, though it comes with the very stigmatizing assumptions\nthat patients’ brains are “broken” and require stimulant drug\ntreatment.[[85]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9131 \"note\")\nSecond, the accommodations many people with ADHD require can be incompatible\nwith what Autistic people need. As an Autistic person without ADHD, I need a\nquiet, private, clean space in order to feel calm and focused. I also need\nsilence and darkness in order to sleep. Many people with ADHD, in contrast,\nrequire stimulation, novelty, and sensory input. They may need the television\nblaring while studying, for example, or may be unable to sleep without music\non. Clutter and mess overwhelms many Autistic people; for many ADHDers “visual\nnoise” is easy to ignore, so much so that messes can “disappear” from their\nfield of view. ADHDer friends often enlist my help looking for their phones\nand keys because they can’t scan through their piles of stuff to find it. To\nthem it’s all just a morass of white noise, but I can instantly locate\nspecific objects at a glance.\n\nMany ADHDers that I know describe themselves as “time blind,” or as perceiving\ntime as moving in a spiral or series of waves. I experience time quite\nlinearly, and rigidly, and have never been late to an appointment or missed a\ndeadline in my life. Writers and creatives who have ADHD tend to work in big\nbursts of late-night passion, and put their work together in an associative,\nbig-picture way. I work on a consistent schedule, analyzing sources and\nputting them together piece by tiny piece. But I also have an impulsive and\nchaotic streak, which might have gotten me labeled ADHD (or Borderline, or\nsomething else) if I hadn’t been better at hiding it when I was young.\n\nA number of the Autistic people I interviewed for this book are also ADHDers.\nSo are many of the writers, mental health providers, and activists I quote.\nWithin the Autistic self-advocacy community, people with ADHD are usually\ntreated as honorary members by default. And the more we learn about the two\nneurotypes, the less they seem like distinct categories. They are, in every\nsense, sibling disabilities, two highly similar groups who belong in community\nwith one another.[[86]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9139\n\"note\")\n\nIn addition to overlapping with many mental disabilities and disorders, Autism\nalso co-occurs frequently with physical disabilities like Ehlers-Danlos\nsyndrome (EDS),[[87]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9147 \"note\")\ngastrointestinal\ndisorders,[[88]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9155 \"note\") and\nepilepsy.[[89]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9167 \"note\")\nHeather Morgan, who has physical disabilities as well as Autism, says we can\nthink of some conditions as sharing Autism’s genetic markers.\n\n“I think there are more of us in that category than we necessarily realize,”\nshe tells me. “[P]eople with disabilities that maybe aren’t typical Autism,\nbut have Autistic characteristics in their genetic sequence.”\n\nWhen Autism intersects with other disorders or disabilities, traits can take\non new forms or be hidden entirely. I’m close friends with the family of\nAngel, an Autistic teenager with traumatic brain injuries and intellectual\ndisabilities. If Angel hadn’t been diagnosed with Autism prior to the car\naccident that caused his brain injury, doctors might never have recognized him\nas Autistic at all. They might have believed, for example, that he couldn’t\nspeak because of neural damage caused by the car accident. If that had been\nthe case, Angel wouldn’t have gotten his augmented communication device, or\nthe iPad he uses to chat with friends on social media. Thankfully, Angel’s\nfamily and care team figured out that his lack of verbal communication wasn’t\ncaused by an inability to express himself, but by an Autistic need for\nnonverbal methods of self-expression.\n\nAngel is a rare example of a masked Autistic person who isn’t viewed by the\npeople around him as “high functioning” or high in intelligence. Of course,\nthe very idea that certain Autistic people function more highly than others,\nor that functioning status is a binary quality you can catch at a glance, is\nproblematic in its own right. That kind of thinking leads to many of us having\nour disabilities erased, and the private suffering that makes public\n“functioning” possible is ignored. It also perpetuates the idea that the only\ndisabled lives worth living are those that can still manage to be productive\nor impressive in some conventional way.\n\n# “Highly Functioning” Autistics\n\nNeurotypical people are obsessed with functioning levels. If you tell a\nnondisabled person that you’re Autistic, but you’re able to hold a\nconversation or maintain a job, they’ll immediately start gushing about how\nfunctional you are. Usually, that remark comes with the implication that you\ndon’t really count as disabled because you can fake a nondisabled status (if\nonly for a moment). When I was doing press for my first book, I received a\nfair share of comments like the following, which was left on a YouTube\nlivestream in which I\nappeared:[[90]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9178 \"note\")\n\n“If Dr. Price is autistic then they are extremely high functioning. Most\npeople with autism spend their whole lives barely able to hold down a job\nbecause they’re unable to meaningfully or appropriately interact with others,\nnor are they able to focus on anything intently for any extended period of\ntime or if they do, it’s something that’s extremely trivial and irrelevant.”\n\nThere is a lot to unpack in this comment. First is the commenter’s assumption\nthat because I seem to function “highly,” my being Autistic is somewhat\ndubious to him. He says “if” I’m Autistic I must be high functioning, not that\nI am Autistic and capable or accomplished. He sees the two things as\nincompatible. Furthermore, he seems to think I don’t really count as Autistic,\nbecause I can feign normality so well during an hourlong conversation. Another\nthing that jumps out is the way he equates holding down a job with having a\nlife of value. In this commenter’s view, I am a high-functioning Autistic\nbecause I can hyperfocus on something that makes money. Autistic passions that\naren’t moneymaking are, as he says, “trivial” and “irrelevant.” That word\n_irrelevant_ is also particularly striking—it’s as if the Autistic person’s\nown feelings and pleasure do not matter at all, only how their life is\nreceived by others.\n\nWhen neurotypical people equate “functioning” with being less disabled, they\nfail to recognize the immense, hidden labor that goes into appearing normal.\nIt also misses just how oppressive having to seem normal is by itself. It’s\nreminiscent of when I see a fat person proudly identify themselves as fat,\nonly to be corrected by a thin person with a dismissive, “You’re not fat!\nYou’re just curvy! You’re so pretty!” That kind of response betrays discomfort\nwith fatness and fat pride, and reveals a latent belief that one can’t be fat\nand beautiful at the same time. But a person can be both fat and beautiful,\nthe two attributes are completely independent of one another. On top of that,\nit’s insulting that a person’s beauty is part of how their value is defined.\nConversely, an Autistic person can function in one (or many) realms of public\nlife, while being significantly disabled in others. Furthermore, some people\ndon’t “function” independently in any area of life at all, and that shouldn’t\ndetract from their value and the respect they receive, either.\n\nThe Instagram account @MyAutisticNurse documents the life of one “high\nfunctioning” Autistic person, a nurse who goes by the nickname\nBoo.[[91]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9186 \"note\") By all\naccounts, Boo is a fantastic nurse; her mind is a repository of medical facts\nthat she can call from memory at will. She’s excellent at working with\npediatric patients and putting them at ease. She also has days when she is\ncompletely unable to speak. After an especially stressful shift at her\nhospital, she spends hours on the floor, lining up her favorite toys over and\nover. Like any other Autistic person, she has meltdowns and low-energy days,\nbut because she’s intelligent and capable, her Autism doesn’t fit the\n“typical” mold.\n\nUntil 2013, the _Diagnostic and Statistical Manual of Mental Disorders_ drew a\ndistinction between Autism and Asperger’s Syndrome. Autism was more profoundly\ndebilitating and associated with major communication deficits and intellectual\nchallenges. Asperger’s, on the other hand, occurred in people with high\nintelligence, and was associated with well-spoken, emotionally frosty math\ngeniuses and computer nerds. The 2013 edition of the _DSM_ folded both labels\ninto one: Autism Spectrum Disorder, or ASD. Today, instead of talking about\nhow Autism differs from Asperger’s, clinicians discuss whether someone is\n“high or low functioning” or what level their “support needs” are.\n\nThe Autistic Self Advocacy Network (or ASAN) and other organizations led by\nAutistic people reject terms like _high functioning_ and _low functioning_.\nThose words oversimplify how a disability affects a person’s life, and equates\ntheir productivity with their value as a human\nbeing.[[92]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9194 \"note\") A person\nwho can speak, socialize, and hold down a job may strike outside observers as\nvery “high functioning”; in private, that same person may need help getting\ndressed, or may require people to remind them when to eat. Boo’s husband, for\nexample, has created an easy-to-read chart listing all the snacks they have\navailable at home, to help Boo process what to do when she is feeling hungry\nand run-down. He also helps motivate her to do things like brushing or washing\nher hair, activities that are both necessary and painful for her.\n\nConversely, a seemingly “low functioning” Autistic person who cannot speak or\ndress themselves may be able to excel in school or solve complex math\nequations, so long as they are provided with accommodations. The writer and\nactivist Ido Kedar spent much of his early life unable to communicate with\nanyone. He couldn’t speak verbally, and his motor control made it difficult to\nwrite. Then he learned to type on an iPad, and his blog “Ido in Autismland”\nwas born. Ido has written two books, given countless interviews, and continues\nto post regularly about Autism and disability justice to his blog. He also\ngraduated from high school with a 3.9 GPA and is currently working his way\nthrough college. Academically and intellectually, Ido functions at a very high\nlevel, now that he has the support to make that possible. Yet because he can’t\nspeak and lacked that support for a long time, he occupied a “low functioning”\nposition in society for many years.\n\nCases like Ido’s and Boo’s really highlight how superficial functioning labels\ncan be. Still, they shape how psychiatrists, teachers, and parents think about\nAutism, and it does tend to be the people considered “high functioning” who\ncan mask the most readily, and who therefore miss getting diagnosed. Generally\nspeaking, if an Autistic person was verbal from a young age and could fake\nsome social niceties, they were likely to either be considered “high\nfunctioning” as kids, or they weren’t identified as Autistic at all. This is a\nbit ironic, because learning to speak at an early age was an early indicator\nof Asperger’s Disorder.[[93]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9202\n\"note\") My mom claims that I said my first word at six months old, and was\nspeaking in sentences by the time I was one. I supposedly shocked a department\nstore clerk as a one-year-old by greeting him and declaring “I believe I smell\npotpourri.” My whole family has tons of stories like these. Many people who\neither were labeled as having Asperger’s in the 1990s or are considered “high\nfunctioning” now have similar stories of being hyperverbal toddlers. It often\nled to us being filtered into gifted education programs rather than special\neducation, which came with both advantages and its fair share of poorly\nboundaried, objectifying experiences.\n\nFor me, and for countless “high functioning” Autistics, communication and\nintelligence become an essential part of our masks. I never could fit in with\nother kids, but I could impress teachers with my grasp of big words and my\nsophisticated-sounding opinions. Though my language was highly developed, my\nsocial and emotional life was not. I annoyed other kids by talking too much\nabout subjects that didn’t interest them. I clung to adults who found me\n“impressive” and equated being well-behaved with being mature and worthy of\ntheir respect. I also absorbed the idea, common to many “gifted” children,\nthat a person’s intellectual potential belongs to society, not to themselves,\nand they owe the world greatness to justify their oddness. In my adolescence,\nEnglish teachers adored my papers, and I excelled on the debate team, but I\nwas brittle and distant to my friends and made all kinds of reckless personal\ndecisions (such as shoplifting and skipping classes that I didn’t like) to the\npoint where I nearly got arrested and expelled. I got so attached to seeing\nmyself as smart and accomplished that I neglected my physical health in the\npursuit of success, too. Until I was in my mid twenties and realized I was\nAutistic, I was basically a perpetual adolescent, performing intelligence for\npraise but mismanaging my personal life and not connecting with anyone in a\ndeeper way.\n\nNylah had a similar experience. “I was a fantastic saleswoman when my life was\nat its most dysfunctional,” she tells me. “I could charm anyone if they didn’t\nget to know me, really know me, and see how much I was drinking and lying to\nprop that life up.”\n\nHiding self-destructiveness behind a mountain of achievements isn’t\nfunctioning, not really. The very concept of “functioning status” is\npredicated on the logic of capitalism and the legacy of the Protestant work\nethic, which both have trained us to believe that a person’s productivity\ndetermines their worth.[[94]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9216\n\"note\") No one is more harmed by this worldview than the disabled people who\ncannot work and produce value at all, and are the most likely to wind up\nabused, forcibly institutionalized, or homeless as a result. Equating a\nperson’s social value (or even their right to exist) with their productivity\nis sadly a common outlook, but it’s also a profoundly alienating and ableist\none. It harms the Autistic people who are able to “play the game” and mask as\nproductive and respectful; for the Autistics who cannot play along, that game\ncan quickly turn dangerous, even deadly.\n\n# Meeting Masked Autistics and Finding Your Place in the Community\n\nSpaces like the Autistic Self Advocacy Network and Autistics Against Curing\nAutism embrace self-realized Autistics, because the community recognizes not\neveryone will have the chance to get a fair or affordable assessment. Plus,\nmany people with subclinical Autistic traits may share common struggles and\ngoals with us, and deserve to be included in our ranks. This includes the\nparents or relatives of diagnosed Autistic children who come to realize\nthey’re on the spectrum as well, and people with “sibling conditions” like\nADHD or PTSD.\n\nI want Autistic people to experience less shame about who they are, and to\nlearn to take off the restrictive masks that have trapped us for decades. The\nfirst step to unmasking is accepting who you are, and finding others with\nsimilar experiences. You don’t need a piece of paper from an assessor to begin\nto do that.\n\nIf you suspect you are Autistic, I encourage you to find a local Autistic Self\nAdvocacy Network (ASAN) chapter, and begin to read writing and watch videos\nAutistic people have posted online. Learn a bit about just how varied our\nexperiences and identities are. As you learn more, you may find you feel at\nhome among us. Or you might find out some other community (such as the ADHDer\ncommunity, or the broader Mad Pride movement) is a better fit. Both outcomes\nare perfectly okay. Even if you conclude you are not Autistic, your self-\nexploration will mean you’ve learned a whole lot about a group that could use\nmore understanding allies.\n\nWhen I was first exploring an Autistic identity for myself, I checked out\nvideos by Autistic creators and activists, who showed me just how varied\nAutistic people can be, both in terms of personality and interests. The more\nAutistic voices I read and listened to, the less Autism felt like a curse. The\nshame I felt about my identity began to ebb, and pride in who I was gradually\nreplaced it.\n\nOnce I had enough confidence to say I resonated with Autistic experiences, I\nput effort into meeting fellow Autistic people in the flesh. I met people at a\nlocal group, Autistics Against Curing Autism, run by Timotheus Gordon Jr. I\nalso attended a local genderqueer support group and where nearly half the\nattendees were neurodiverse. I posted on Autism support groups online, like\nthe subreddit r/AutismTranslated, and got to know others like me in those\nways. These connections to the Autism self-advocacy world wound up doing far\nmore for me than the psychological establishment did. Establishing official\nrecognition of my disability was challenging, bureaucratic, and ultimately\nfelt very hollow and meaningless—much like getting legal recognition of my\ngender. I was Autistic long before any professional recognized it, just as I\nwas trans long before the state acknowledged it. However, nothing aided me in\naccepting myself and unmasking quite like finding my “people” and seeing proof\npositive that there was nothing wrong with us.\n\nIf you suspect you might be Autistic, I hope you can seek out similar spaces\nand resources for yourself. ASAN has chapters in many major cities, and online\nAutism groups are filled with supportive people who love to answer questions\nand share their own stories. On most social media sites, the #ActuallyAutistic\nand #AdultAutistic tags are filled with useful posts. You might also wish to\nseek out tools created by Autistic people, for Autistic people. For example,\nweighted blankets or fidget toys sold by sites like Stimtastic might help\nsoothe your anxiety. Or the social skills toolkits offered on blogs like\nRealSocialSkills.org may help you develop greater confidence in interacting\nwith people, disabled and neurotypical alike. It is not cultural appropriation\nor “faking a disability” to try out these tools. If Autism-friendly resources\nand adaptations prove helpful to you, that’s another key signal you belong in\nour spaces, or at the very least have a great deal in common with us.\n\nUltimately, I can’t tell you if you are Autistic, and I don’t necessarily\nthink it’s something we have to discuss in a binary or categorical way. Autism\nis a spectrum, a rainbow of different shades and hues that thrive when they\nstand beautifully together. For too long we have hidden what makes us unique,\nfearing we’re broken or unlovable. Embracing Autism means shedding that mask\nand finding safe ways to share our vibrant colors with the world.\n\nIn the next chapter, I’ll explain how the ableism, sexism, and white supremacy\nlurking behind early Autism research created the pressure for so many of us to\n“mask.” I’ll outline what the gradual development of the mask looks like over\nthe course of an Autistic person’s early life, and discuss the science on what\nmasking really is and what psychological processes undergird it. I’ll provide\nsome tools and exercises for investigating your own mask, and where it might\nhave come from. We’ll also reflect on the psychological and emotional costs of\nmasking. In the chapters that follow, I’ll introduce you to Autistic people\nwho are slowly unlearning Autism stigma and taking their masks off, and\nprovide some tricks and tips developed by Autistic coaches, counselors, and\nactivists. We’ll also discuss some public policy changes that would help\nAutistic people and other neurodiverse groups attain justice. As the next\nportion of the book will outline, masking is just as pervasive as Autism is.\nIt’s much more than faking a smile—it impacts how we identify, how we dress,\nthe careers we choose, our relationships, and even how we lay out our homes.\nWhen we unmask, we get to reexamine every choice that we’ve made to “fit in,”\nand begin to construct more authentic and affirming lives. A world that is\nmore tolerant of difference is a safer and more nourishing place for everyone.\nAnd we can begin to build that world today, simply by questioning the ways\nwe’ve been forced to live, and choosing instead to exist proudly as ourselves.\n\n"
      }
    ]
  }
]

---

### User
> 12/1/2025, 1:49:24 PM

[
  {
    "tool_use_id": "toolu_012Mvg8BAaFZCpYZHUXYZdb5",
    "type": "tool_result",
    "content": [
      {
        "type": "text",
        "text": "# CHAPTER 3\n\n# The Anatomy of the Mask\n\nUndiagnosed and clueless about the root of her challenges, Crystal had to\nsuffer in silence throughout childhood. As her grandfather observed, she was a\nwell-behaved, sweet kid, and a total teacher’s pet. Yet behind her smiling,\nagreeable façade, she was coping with constant social confusion and\nloneliness. In classes where instructions weren’t always clear, like science\nand math, she floundered. At school, she socialized with other girls, but she\nrarely got invited to sleepovers or outings to the mall or skating rink. She\nkept her head down around other people, and at home complained of frequent\nstomachaches and threw “tantrums” out of stress. By middle school, it was\nimpossible for her to ignore how difficult she found regular life.\n\n“Once you get to middle school, you have this really complicated class\nschedule you have to follow. All these transitions, bells going off, everyone\nswitching classrooms every hour, after school-activities, busy busy busy. I\ndon’t do well with shifting gears; it takes a ton of energy for me now and I\nwas suddenly having to do it all day.”\n\nMany Autistic people find it challenging to transition between activities.\nEach change requires a lot of what psychologists call executive functioning, a\nskill linked to planning and initiating\nbehavior.[[1]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9229 \"note\") Most\nAutistics find it relatively easy to give a task we enjoy our unbroken\nattention, but we find it challenging to gear shift. Crystal could sit reading\na book for hours without interruption, but in middle school classes switched\nso often that by the time she adjusted to a new room and settled into paying\nattention, it was time to move again. Middle school was also socially\noverstimulating: she went from sharing a classroom with fifteen children she’d\nknown all her life to suddenly having to learn dozens of new names, faces, and\ninterlocking social dynamics.\n\nFriendship gets way more complicated and fraught as a preteen, and so do all\nthe expectations placed on you. The adults aren’t as kind and gentle as they\nonce were. If you take a long time to figure something out, they assume you’re\ndragging your feet out of adolescent apathy rather than executive functioning\ndifferences. If you have problems making friends, it’s because you’re a moody\nteen, not because neurotypical conversation rules are inscrutable to you. For\nCrystal, and for a lot of masked Autistic people, middle school is when a lot\nof struggles really come to the fore. Then puberty hits, and you have to get\nused to a shifting and unfamiliar body, and a whole new slew of disturbances\nfollow.\n\nAll Crystal knew at the time was that the school bells stressed her out and\neverything was moving too quickly. She felt like she was moving at half speed,\nwhile everyone around her was a blur. It was hard for her to keep track of\nwhich interests she had faked around which people, and which personality she’d\nadopted to win over each teacher. She began to burn out, so her cognitive and\nsocial functioning declined even\nmore.[[2]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9237 \"note\") Now she\ncouldn’t even push herself through the school day. All she wanted to do was\nfind a private place to lie down and vegetate. No one had noticed yet that she\nneeded help. So, she started begging her mom to let her skip school.\n\n“It was really hard to convince my mom to let me stay home that much,” Crystal\nsays. “And eventually I hit the limit of how many sick days I could have\nwithout getting in trouble. But for as long as I could I got ‘stomachaches’\nand stayed home, which really kept me sane.”\n\nFor Crystal, faking sickness was an essential part of her mask. It could get\nher out of the overstimulating classroom and provide her some much-needed\nrest. Mirroring her female classmates and pretending to like what they liked\nwas an act of masking, too. And as school became more and more challenging,\nCrystal started masking in new ways, like pretending she didn’t care about\n“boy” subjects like science and math.\n\n“There were girls around me who were getting interested in makeup and fashion,\ndating boys, celebrity gossip,” Crystal says. “I could play along with that\ntoo…. The cool vapid girl vibe was a shield for being confused by all the\nrandom symbols in algebra that no teacher explained to me and just assumed I’d\nfigure out. Instead of admitting I didn’t understand what the hell was going\non I could flip my hair and say _this is so boring, let’s talk about something\nthat matters, like_ _Mariah Carey dating Eminem_.”\n\nCrystal had already observed that if she asked for help with something that\nneurotypical people found “obvious,” she wouldn’t get assistance. They’d just\nfind her exhausting, or think she was asking questions just to waste time. But\nCrystal genuinely didn’t know what role _x_ played in a linear equation. She\ndidn’t understand what “show your work” meant in a math context, so she’d\nwrite long paragraphs explaining her thought process in words, and describing\nexactly which buttons on the calculator she’d pressed. Her teacher took this\nas some kind of personal insult, and wrote Crystal up for it. She cried in the\ndetention hall the entire time, baffled that her best attempt at showing her\nwork had somehow been rude.\n\nThere were also elaborate rules about how middle-school-aged kids were\nsupposed to act, but Crystal only ever found out about these rules when she’d\nbroken one of them egregiously. Like the time she wore a painfully uncool tie-\ndyed T-shirt from JCPenney to school and the other girls wouldn’t quit\nlaughing at it.\n\nCrystal says, “I had to become almost a cartoon of vapid femininity to explain\nwhy I was so out of it. I couldn’t be good at being a person, but I could be\ngood at being a _girl_. And my girly-ness could explain why I was so dumb at\nmath and so bad at people. _She’s just a ditz_.”\n\nTimotheus Gordon Jr. tells me that when he was a child, he had to learn to\nmask his youthful sensitivity and hide his nerdier interests, presenting as\ntougher and cooler than he actually felt inside.\n\n“In my community, crying is a sign of weakness, and I could be targeted for\nbeing weak, so early on I had to mask my sadness with aggression and learning\nhow to fight,” he says. “When it came to having interests like social\nsciences, history, and more geeky stuff like Pokémon, I had to hide it because\nthat was considered to be uncool and a weakness.”\n\nAs was true in Crystal’s case, gender roles and ableism both conspired and\npushed Timotheus to hide the parts of himself that his neurotypical peers\nwould look down on and punish. He could play up his more gender-normative\ninterests, such as his love of football (with all its statistics and player\ntrivia to memorize), but anything that marked him as too sensitive, odd, or\nnot sufficiently masculine was risky.\n\nUnlike Crystal, however, Timotheus’s experiences as a masked Autistic are also\ninseparably tied to anti-Black racism. Though he now has many authentic\nrelationships rooted in like-mindedness and shared nerdy interests, he still\nhas to worry about being perceived unfairly as he moves throughout the world.\nHe doesn’t just have to worry about being seen as weak as he did as a\nchild—out among white people and in white institutions, he has to fear being\nseen as too aggressive.\n\n“Even my mannerisms like speaking bluntly or directly, or matter-of-fact. I\nstill have to mask because I want to tell the truth. But it’s not about what I\nsay, it’s about what people interpret. And I have gotten into trouble because\nof what people interpret.”\n\nI think for most masked Autistic people, there are key moments in childhood or\nadolescence where we learn we are _embarrassing_ or _wrong_. We say the wrong\nthing, misread a situation, or fail to play along with a neurotypical joke,\nand our difference is suddenly laid bare for all to see. Neurotypical people\nmay not know we’re disabled, but they identify in us some key flaw that is\nassociated with disability: we’re childish, or bitter, self-absorbed, or too\n“angry,” or maybe we’re just awkward and make people cringe. Avoiding being\nseen in these ways becomes our core motivation in life, each day a battle\nbetween the heavy armor we wear and the embarrassing characteristics that\narmor was designed to cover up.\n\nFor me, masking was always about not seeming childish. When I was a kid, I was\nforever getting corrected for acting like a baby, and that mortified me. When\nI was disgusted by the textures of the unfamiliar food at sleepaway camp and\nwent into a full-blown, sobbing meltdown over it, I got reprimanded for being\na picky eater and a crybaby, and was forced to sit at the table all evening,\nuntil I gulped some cold ravioli down. When I failed to learn how to ride a\nbike at the “correct” age because I had poor balance and motor control, my dad\nshamed me for my immature clumsiness (perhaps because it reminded him of his\nown masked motor disability). As an adult, I would cuddle with stuffed animals\nat night with the blinds pulled down low and my bedroom door double locked,\nfearing that someone might walk past the house or into my room and discover\nthe terrible fact that holding soft, cute things brought me comfort.\n\nThe fear of seeming childish wounded me in a profound way, as it does many\nAutistic folks. One of the major ways abled society dehumanizes the disabled\nis by calling our maturity into question. “Adults” are supposed to be\nindependent, though of course no person actually is. We all rely on the hard\nwork and social-emotional support of dozens of people every single day. You’re\nonly seen as less adult, and supposedly less of a\nperson,[[3]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9248 \"note\") if you\nneed help in ways that disrupt the illusions of self-sufficiency.\n\nNeeding help with toileting, for example, reminds abled people of the fact\nthat they once wore diapers, too, and that one day they might need diapers\nagain. People who need help toileting are vulnerable, and reliant on others.\nThat fact distresses and repels the nondisabled, and they cope with their hard\nfeelings by framing those who wear diapers as essentially different from\nthemselves. They’re perpetual children, inhuman incompetents, not someone to\nempathize with. My own “childishness” reminded allistic people that much of\nwhat we call maturity is a silly pantomime of independence and unfeeling, not\na real quality of unbreakable strength. Abled people hated seeing my awkward\nsoftness and confronting the fact they might be sensitive and needy in their\nown ways, too. So they acted like I was invisible, or that my childlike habits\nwere perverse. I learned that feigning maturity would be my sole salvation,\nthe only way to ensure my humanity got recognized.\n\nAs I grew older, I overcorrected for secretly being “childish” and\n“embarrassing” by adopting a façade of jadedness and hyperindependence. Though\nit manifested in a slightly different way than it did for Timotheus, I made it\nmy goal to always seem tough. I made fun of my friends, rolled my eyes a lot,\nand acted like I was too cool to care about anything. I tore down other people\nfor liking “babyish” things, like boy bands and cartoons. I refused to cry in\nfront of anybody, and resented anyone who did express emotions openly. I told\nmyself I’d never get caught being a baby ever again. That commitment meant\nnever asking for help at all.\n\nIf you’re a masked Autistic, or suspect you might be, you probably can recall\nexperiences like Crystal’s, Timotheus’s, and mine. I think examining the\norigins of your mask can help you identify some of the deep-seated fears that\ndrive your need to wear it. Are you afraid of seeming stupid? Or childish?\nWhen you were young, did people accuse you of being cruel? Did you come to\nbelieve you were finicky, or selfish?\n\nAutistic people frequently are stereotyped as immature, unintelligent, cold,\nor out of touch. And each of our masks helps to cover up the Autism\nstereotypes we felt we needed to resist the most. Behind each mask, there sits\na deep pain, and a series of painful beliefs about who you are and what you\nmust never allow yourself to do. Consequently, a big part of unmasking will\nmean facing those qualities you loathe the most in yourself, and working to\nsee them as neutral, or even as strengths.\n\nHere’s an exercise to get you thinking about where your mask comes from. Many\nof the negative qualities associated with Autism that we explore here will\ncome up again later, in exercises focused on reexamining your self-concept and\npracticing unmasking.\n\n# Reflecting on the Need to Mask:\n\n## What Does Your Mask Protect You From?  \n  \n---  \n1\\. Try to recall a time early in life when you felt intense embarrassment or\nshame. Describe that situation here. 2\\. When you recall this experience, what\nemotions do you feel? 3\\. Complete the sentence by checking off as many\nadjectives as you like: “In that moment, everyone could see that I was\n_______.” ____ Selfish ____ Robotic ____ Awkward ____ Immature ____ Childish\n____ Disgusting ____ Self-absorbed ____ Embarrassing ____ Cold ____ Clueless\n____ Stupid ____ Cruel ____ Weak ____ Pathetic Other:\n_____­_____­_____­_____­_____­_____­_____­__ 4\\. Of the words listed above,\nwhich one is the most _painful_ to hear associated with you? 5\\. List some\nactions or habits that you associate with that word. 6\\. Complete this\nsentence: I pretend to be _____­_____­ so that people will tolerate me, but\ndeep down I know that I’m not. ____ Independent ____ Happy ____ Cool ____\nConfident ____ Generous ____ Caring ____ Mature ____ Organized ____ Warm ____\nSmart ____ Impressive ____ Powerful ____ Helpful ____ Worthy Other:\n_____­_____­_____­_____­_____­_____­_____­__ 7\\. Complete the sentence: “If I\nwant people to like me, I can’t let them find out that I _____­_____­.”  \n  \nTo download this chart, go to <http://prhlink.com/9780593235249a003>.\n\nNow that we’ve explored what Autism really is, gotten the chance to meet some\nmasked Autistics, and reflected on the social and structural forces that drive\nthe need to mask, let’s dive into the science behind what masking really is.\n\n# What Is Masking?\n\nIn the psychological literature on the subject, Autism masking is said to\nconsist of two classes of\nbehavior:[[4]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9256 \"note\")\n\n**_Camouflaging_** : attempting to hide or obscure Autistic traits in order to\n“blend in” with neurotypicals. The main goal of camouflage is to avoid\ndetection as disabled.\n\n**_Compensation_** : using specific strategies to “overcome” challenges and\nimpairments related to disability. The main goal of compensation is to\nmaintain the appearance of high, independent functioning.\n\nWhen Crystal attempted to disappear into the social background by making\nherself agreeable and passive, she was camouflaging how confused and\noverwhelmed she was. When she studied up on celebrity gossip so she’d have\nthings to discuss with her friends, she was compensating for her comparative\nlack of neurotypical conversation skills. Some of Crystal’s masking behaviors\nwere a blend of both compensation and camouflage: faking being sick allowed\nCrystal to hide how exhausted and overloaded she was (in other words, it\ncamouflaged these needs), but it also provided her a neurotypical-approved\nexcuse for getting the breaks she required (which allowed her to compensate\nfor her exhaustion). Camouflage is all about obscuring one’s unique qualities\nand struggles as a disabled person; compensation is all about crafting little\nhacks and cheats to help you get your needs met because you can’t request the\naccommodations you require. Playing up an interest in football because it was\nsocially acceptable and gender conforming, for instance, was a compensatory\nstrategy that served Timotheus well.\n\nAll masked Autistics employ both compensatory and camouflaging strategies to\nhelp us get by, and apply them to a wide variety of tasks we find challenging.\nSomeone might verbally camouflage by forcing themselves not to speak too much\nabout their special\ninterests,[[5]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9267 \"note\") for\nexample, and socially compensate by researching a friend’s Facebook posts\nbefore meeting up with them, so they’ll have a good idea of what to chat\nabout.[[6]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9275 \"note\") A person\nmight camouflage their auditory sensitivities by gritting their teeth through\nthe pain and never complaining about it, or they might compensate for it by\nwearing subtle noise-canceling earbuds that don’t stand out as unusual.\n\nWhen I introduce neurotypical people to the concept of Autism masking, they\nusually understand it as a social process or performance. It’s true that\nmasking involves things like memorizing social rules and feigning\nfriendliness, but that’s really just the most obvious form it takes. Most of\nus have to mask everything from our information processing style, to our lack\nof coordination, to our limited food preferences, to the fact that we require\nmore rest than neurotypical people are expected to. Masking shapes the fields\nwe work in, how we dress and carry ourselves, where we live.\n\nMany maskers choose careers that allow them to hide their executive\nfunctioning issues. Or they realize they have no choice but to freelance\nbecause they can’t keep up with all the meetings and socializing a full-time\njob requires. I was initially drawn to academia because I believed it was a\nplace where I could dress however I liked, keep my own hours, and be eccentric\nwithout consequence. I knew I’d never have the energy or patience to fake\nbeing professional by corporate standards, so I compensated by developing\nskills and credentials that would allow me to be valued for my mind rather\nthan my looks or poise. Many Autistic people who work in tech gravitate to the\nfield because Autism spectrum traits are somewhat normalized there. Multiple\nneurodiverse people who do sex work reported to me that the flexible hours and\nthe potential of making rent within a few days of work made the career a good\nfit for them.\n\nMasked Autistics tend to arrange our lives around our limitations and needs,\nand sacrifice anything that might demand too much energy out of us. An\nimpressive resume or academic transcript might hide the fact our homes are\nmessy, our hair is unbrushed, and we haven’t socialized with anybody\nrecreationally in months. In a few key areas we may appear to be functioning\nhighly, but that façade requires we let everything else in life fall apart.\n\nMy friend Jess once described their compensation this way: “It’s like going to\nthe grocery store, but only being able to bring home what you can sneak into\nyour pockets when nobody is looking. And everybody else gets to just go\nthrough the checkout and buy as much as they want, so they don’t understand\nwhy you find shopping stressful.”\n\nJess has ADHD, but their description of how challenging it is to lie, cheat,\nand steal your way through a neurotypical-looking life when you lack the\naccommodations you need is just as relevant to life as a masked Autistic\nperson. Regular life is more cognitively and emotionally demanding for\nneurodiverse people than it is for neurotypicals, but we have to hide that\nfact from other people on a daily basis. To prop up our façade of being “high\nfunctioning,” we build a messy, unstable scaffolding of flawed coping\nmechanisms. It’s no wonder we report\nanxiety[[7]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9283 \"note\") and\ndepression[[8]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9291 \"note\") at\nelevated rates. If the only food you ever get to eat is what you can steal,\nyou’re gonna move through the world feeling undernourished and hypervigilant.\n\nThough masking is incredibly taxing and causes us a lot of existential\nturmoil, it’s rewarded and facilitated by neurotypical people. Masking makes\nAutistic people easier to “deal” with. It renders us compliant and quiet. It\nalso traps us. Once you’ve proven yourself capable of suffering in silence,\nneurotypical people tend to expect you’ll be able to do it forever, no matter\nthe cost. Being a well-behaved Autistic person puts us in a real double bind\nand forces many of us to keep masking for far longer (and far more\npervasively) than we want to.\n\n# The Double Bind of Being “Well-Behaved”\n\nPsychiatrists and psychologists have always defined Autism by how the\ndisability impacts neurotypical people. A more “severely” Autistic person is\nnot necessarily a person who experiences more interior suffering, but rather\nsomeone who suffers in a more disruptive, annoying, or disturbing way. The\nAutistic children who present the biggest hassle are the ones most likely to\nbe referred to services, whereas those who can conceal their struggles are\ngranted tentative approval—but risk never being understood or empathized with.\n\nResearchers Zablotsky, Bramlett, and Blumberg set out to understand how\nparents perceive the “severity” of their Autistic kids’\nsymptoms.[[9]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9299 \"note\") They\nsurveyed nearly a thousand families raising Autistic kids, and also measured\nthe Autism symptom severity of the children themselves. What the researchers\nfound was that parents did not accurately perceive the level of their kids’\nsuffering. Instead, parents based their ratings of Autism “severity” on how\nmuch their kids’ behavior bothered them and required a lot of their time and\nattention. Many children described by parents as “high functioning” were\nquietly coping with debilitating sensory pain, or were falling behind\nacademically or socially in significant ways. This carries over to how\nAutistic adults are perceived, and the expectations that neurotypical\ninstitutions place on us to appear “normal.”\n\nThis desire to make Autistics compliant and nondisruptive is a large part of\nwhy the prevailing treatment for Autism in children is Applied Behavior\nAnalysis (or ABA) therapy. ABA is focused on training Autistic kids to fake a\nneurotypical personality. It’s a behavioral therapy, not a cognitive or\nemotional one. As long as the Autistic child’s outward actions change and\nbecome less “disruptive” or more “normal,” it doesn’t really matter to the ABA\ntherapist what’s going on between the kid’s ears.\n\nABA therapists train children to camouflage their Autistic traits using a\nsystem of rewards and punishments. ABA patients get sprayed in the face with\nwater (or on the tongue with vinegar) for failing to make eye contact, or for\ntalking too much about their special interests. If a child engages in\necholalia (phrase repeating), chews on their fingers, or flaps their hands,\nthey’ll be punished, even if they find these impulses painful to restrain. ABA\npatients are also forced to rehearse compensation strategies. They’re made to\nsit still for hours until they parrot back a conversational script correctly,\nand aren’t allowed to get up and play until they provide an “adequate” amount\nof eye contact.[[10]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9313 \"note\")\nThey may be asked to repeat conversational niceties like “please” and “thank\nyou” over and over until they hit on the correct tone of voice, or be told to\nstand up and sit down repeatedly while the therapist snaps their fingers at\nthem like they’re a trained dog. When Autistic kids act out or demand\nattention, ABA therapists are supposed to withdraw, leaving the room or\nignoring their distress. This teaches the Autistic child not to expect any\nhelp from the outside world.\n\nABA therapists also punish children by electrocuting\nthem.[[11]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9321 \"note\") The\nelectroshock devices used in ABA therapy were briefly banned by the Food and\nDrug Administration\n2020,[[12]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9330 \"note\") before\nbeing reinstated in\n2021.[[13]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9338 \"note\") Today,\nthe Association for Behavior Analysis still vocally supports the use of such\n“aversives” to discourage visibly Autistic behavior. In 2012, an ABA-trained\nspecial education teacher came under fire for coating her young students’\ncrayons in hot sauce, to discourage\nchewing.[[14]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9346 \"note\") That\ncase wasn’t a random act of violence. It reflects the core philosophy of ABA.\nThe founder of ABA, Ole Ivar Lovaas, used to coerce children into providing\nhugs and kisses to their therapists by giving them\ncandy.[[15]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9354 \"note\")\n\nForty-six percent of Autistic adults who underwent ABA therapy as kids report\nhaving Post-Traumatic Stress Disorder (PTSD) as a result of the\nexperience.[[16]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9362 \"note\")\nMany experience deep shame even naming the subjects they feel passionate\nabout, because they’ve been punished for having special interests. Some are\nunable to appreciate the emotional and psychological benefits of fidgeting or\nstimming because the importance of having “quiet hands” was so deeply drilled\ninto them. Many don’t know how to refuse an unreasonable demand, or how to\nexpress emotions like anger or fear. One former ABA therapist confessed on an\nanonymous blog that she worries she conditioned her patients to be easy to\nmanipulate and abuse.\n\n“Upset about being treated like a circus animal? Not my problem, kiddo,” she\nwrites. “I’m here to lure you with candy and manipulate you into doing my\nbidding, no questions asked. Which will make you excellent prey for sexual\npredators, abusive teachers, caregivers, and partners later in\nlife.”[[17]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9370 \"note\")\n\nDespite how loathed ABA is by Autistic people, the parents and teachers of\nAutistic kids tend to love it, and research broadly deems it “effective.” This\nis because the efficacy of the program is based on the neurotypical gaze, not\nhow the Autistic child feels. ABA does teach Autistic kids to quiet down and\nbe less annoying and “weird.” The problem is, it does so by training them to\nhate themselves and obey all adults. It’s akin to evaluating how “effective” a\ndepression treatment is by asking the depressed person’s boss how they are\nperforming, rather than checking in with the depressed person themselves.\nSadly, the comfort and convenience of the neurotypical teachers and parents\nare prioritized, so ABA remains the one and only “evidence-based” treatment\nfor Autism that most insurance plans will cover. Becoming “well behaved” is\nmore important than being psychologically well.\n\nFor many Autistic kids, learning to obscure your pain often becomes a primary\nsurvival strategy; for masked Autistics, this isn’t taught within ABA therapy,\nbut as part of regular life. I didn’t go through ABA, but friends’ parents did\nyell at me for squirming awkwardly in my seat. No one forced me to rehearse\n“normal” conversational scripts, but kids laughed and walked away from me when\nI spoke in an inappropriately loud voice or quoted movies to express how I\nfelt. My Girl Scout leader shamed me in front of the whole troop for years\nbecause I always sat with my knees pressed to my chest. My body craved the\npressure of sitting in a curled up, “gargoyle” posture (many Autistic people\nenjoy sitting this way), but the group leader found it so irritating she\ncouldn’t help but berate me for it in front of the whole troop every single\ntime it happened.\n\nAutistic educator and social equity consultant ChrisTiana ObeySumner has\nwritten about an eerily similar experience of having her Autistic traits\npublicly shamed in Girl\nScouts.[[18]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9378 \"note\")\n\n“One of my stimming activities is that I suck my thumb, and put my forearm to\nmy face to both smell my natural scent and feel the soft hairs brush up\nagainst my nose,” she writes. “For some reason, this rubbed my scout leader\nthe wrong way when I was around 7 or 8 years old. She called all of the other\nchildren to circle around and hurl insults at me.”\n\nEvery masked Autistic person has a litany of experiences like this. Most\nmaskers dodge the massive psychological bullet that is ABA therapy, but we\nstill receive endless conditioning that says our unfiltered selves are too\nannoying, unusual, awkward, nonconforming, and cold to fit in. We also witness\nhow other nonconforming bodies and minds are treated. When the entire world\nshames people for being into “childish” things, having odd mannerisms, or\nsimply being irritating, you don’t need ABA to program you into compliance.\nEveryone around you is already doing it.\n\nI still remember the first time I consciously compared myself to a more\n“typically” Autistic person, and realized I needed to hide who I was. It was\nmiddle school, and I was sitting in the cello section a few feet away from\nChris, a percussion\nplayer.[[19]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9387 \"note\") Chris\nand I were both in the same special education gym class; I was there because I\nwas uncoordinated and had abnormally slow reaction times, and my muscles were\nincredibly weak, though no one figured out this was due to Autism. Chris, on\nthe other hand, had been diagnosed when he was very young.\n\nChris was smart and chatty. He loved sharing World War II trivia with people.\nHe’d ask questions in class that seemed to come out of nowhere, and sometimes\nwould involuntarily do a stiff-armed wave to stim, which (because of his World\nWar II obsession) people read as a Nazi salute. Kids laughed at him, teachers\ncondescended to him, and school administrators treated him like a problem to\nbe contained. He was the first Autistic person I ever knew, and how he was\ntreated was instructive to me.\n\nThat day in orchestra class, I was already on edge and annoyed by how loud\neveryone was. Percussionists were whipping drumsticks around; viola players\nwere gossiping and laughing; violinists were tuning their instruments, filling\nthe air with screeching, high-pitched peals. I coped by folding my arms tight\nacross my chest and screwing a pissed-off expression onto my face. The\ngrimacing, somewhat irritated expression that Autistic climate activist Greta\nThunberg is now famous\nfor[[20]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9392 \"note\") is very\nsimilar to how I used to react to loud noise and social chaos. I had already\nstarted to cultivate a grumpy, goth persona to protect me from seeming weak.\nInstead of showing that I was overwhelmed, my mask told other people to stay\nfar away.\n\nChris didn’t have that option. He couldn’t mask how upset he was by the\nnoisiness of the orchestra room. He was jittery and visibly agitated, slamming\nhis music stand up and down on the ground, trying to get his anxiety out.\nPeople laughed at his unease and tried to provoke him by asking him questions\nthey knew he wouldn’t understand.\n\n“Hey Chris,” an older boy hollered. “Do you spit or swallow?”\n\nChris kept slamming the music stand up and down while he looked off into space\nand pondered. “I guess I do both,” he answered sincerely, not grasping the\nsexual implication. He interpreted it as a literal question about whether he\never spit or swallowed at all. People cackled and looked away. Chris’s whole\nbody was tense. He knew he’d stepped on some conversational land mine the\nolder boys had planted.\n\nThen some prankster pulled the fire alarm, and the already loud room filled\nwith clanging bells and kids yelling. There was laughter and mayhem as\neveryone headed for the door. I felt sick to my stomach and furious, but able\nto hide behind my mask of wincing pissed-off-ness. Chris, on the other hand,\nhad booked it out of the room. School administrators found him circling the\ntrack outside, dashing and breathing heavily. Through the windows, we watched\nas the adults tried to reassure him there was no fire, that he was safe. But\nit wasn’t the fire that was bothering him. It was the noise, and the people.\nIt took them an hour to coax Chris back inside.\n\nThough everyone at school knew Chris was disabled, they had no patience for\nhis actions. Administrators groaned as they tried to get him to calm down; my\nclassmates and I joked while he kept awkwardly circling the track. We all saw\nhim as hopelessly immature and embarrassing. I recognized a much-loathed,\ndeeply buried part of myself in Chris, and I hated him for it. I thought I was\nbetter than Chris. I could “keep it together.” I took pride in the fact that\nno one would ever catch me being nervous and weak. I remember being disgusted\nand fascinated by Chris in equal measure. I kept my attention pinned to him\nduring every orchestra class after that, picking apart every quality in him\nthat I needed to hide. I began to surround myself even more thoroughly in a\ncamouflage of frostiness and rage.\n\n# Masking as Overcorrection\n\nFor many masked Autistics, the best way to camouflage a socially undesirable\nquality is to rebound into the complete opposite direction, and overcorrect\nfor anything neurotypical people and institutions have taught us to hate about\nourselves. An Autistic person who was mocked for being needy and intense as a\nchild may camouflage as hyperindependent and emotionally avoidant, for\nexample. On the flip side, an Autistic person who has repeatedly been told\nthey are selfish and robotic might instead wear a mask of helpful\nfriendliness, and become a compulsive people-pleaser or teacher’s pet. We\ninternalize many of the values of the ableist society we’re living in, and\nproject those values both at other disabled people and at\nourselves.[[21]](Pric_9780593235249_epub3_nts_r1.xhtml#en_d1e9400 \"note\")\n\nAfter the incident with Chris, I put excessive effort into hiding everything\nabout me that might reveal I was disabled. I avoided showing enthusiasm or\nstrong emotions for fear of seeming “cringey” and immature. I shut up about my\nobsessive interest in fruit bats and video games. I put on headphones and\nsunglasses when I went out in public, and didn’t look anybody in the face. I\nimpressed teachers with my wit and racked up debate trophies and merit-based\nscholarships, which fed into my sense that I was better than other people, and\nthat my intelligence was the real reason I was alone. I dished out so much\nforceful social aggression that no one could think about challenging me. In\nold home movies from that time, I mock my friends and upbraid them for showing\nexcitement or innocence. It was a cruel act that only made me harder to love,\nbut I performed it perfectly. Until, like many masked Autistics, I finally\nrealized the mask was taking far more from me than it ever gave, and that if I\nwanted to stay alive, I’d need to let it drop.\n\nIn the table below, I’ve listed some of the most common negative stereotypes\nof Autistic people, and the opposing qualities often used to camouflage and\novercompensate against them. As you read through the list, you can reflect a\nbit on the traits that were encouraged in you as a kid, and which qualities\nyou did your damnedest to avoid. I’ve also listed some common behaviors that\ngo along with each masking strategy, and left some blank space, so you can\nfill in your own examples. You may want to revisit your responses to the\nexercise at the top of this chapter, to help you reflect on which needs and\nfears shaped your own need to mask.\n\n# I was taught it was bad to be:\n\n|\n\n# So I had to pretend to be:\n\n|\n\n# I did this by behaving this way:\n\n# (add your own using the blanks)  \n  \n---|---|---  \nArrogant |  Humble |  • Pretending I didn’t know the answers to questions • Keeping silent when people said things that weren’t true • Softening statements with phrases like “if that makes any sense” or “maybe” to make myself sound less certain • • •  \nCold & Unfeeling |  Warm & Friendly |  • Smiling all the time no matter how I felt • Asking people about their feelings and not talking about myself • Taking care of other people whenever they were upset • • •  \nAnnoying & Loud |  Agreeable & Quiet |  • Only experiencing big emotions in private • Solving problems by myself • Not getting “too excited” about anything, including good things • • •  \nChildish |  Mature |  • Serving as a confidant for adults and authority figures • Carrying myself in a restrained, “proper” way • Acting like a “teacher’s pet” or “little professor” and distancing myself from my peers • • •  \nAwkward |  Cool |  • Withdrawing from any activity I wasn’t instantly good at • Pretending to be aloof and uncaring • Rehearsing fake conversations in my mind so I could make talking to people seem effortless • • •  \nClueless, Pathetic |  Independent |  • Nodding or laughing, even when I have no idea what’s going on • Developing unique, private habits and “hacks” that make it possible for me to hold my life together • Making sure my life looks “put together” on paper, even at the expense of my health or happiness • • •  \nSensitive |  Strong |  • Not voicing my needs • Feeling ashamed whenever I wanted to cry or express anger • Fighting internally with every “disruptive” emotion I felt • • •  \nWeak |  Tough |  • Mocking or being aggressive with other people • Thinking of myself as superior to others • Showing distaste for anything society considers feminine, soft, or tender • • •  \nWeird |  Normal |  • Studying what other people like in a systematic, analytical way • Imitating people or characters’ mannerisms, style of dress, tone of voice, etc. • Mocking those who are more obviously “weird” than I • • •  \n  \nTo download this chart, go to <http://prhlink.com/9780593235249a007>.\n\nThere are massive psychological consequences to adopting strategies like\nthese, which go way beyond the anxiety, depression, and burnout we’ve already\ndiscussed. To maintain their masks and compensate for the challenges they’re\nfacing, many Autistic people fall back on an array of destructive and\ncompulsive coping mechanisms, including substance abuse, calorie restriction,\nexcessive exercise, emotional codependency, and even joining cults. I think if\nwe want to really confront the role the mask has played in our lives and work\non parting with it, it’s important we face just how unsustainable and costly\nmasking has been. We sacrifice a lot of our well-being and individuality in\norder to seem “normal.” In the next chapter, I’ll review the research showing\nhow damaging that is, and share the stories of a few Autistic adults who’ve\nbegun to question whether all the effort they’ve been putting into\ncompensation and camouflage has really been worth it.\n\n"
      }
    ]
  }
]

---

### Assistant
> 12/1/2025, 1:49:32 PM

[
  {
    "type": "tool_use",
    "id": "toolu_01T2JntC5ZVPQC81L7x3nXK1",
    "name": "TodoWrite",
    "input": {
      "todos": [
        {
          "content": "Locate Barkley and Price ebooks in filesystem",
          "status": "completed",
          "activeForm": "Locating Barkley and Price ebooks in filesystem"
        },
        {
          "content": "Extract table of contents from both books",
          "status": "completed",
          "activeForm": "Extracting table of contents from both books"
        },
        {
          "content": "Read relevant chapters on ADHD dimensions and assessment",
          "status": "completed",
          "activeForm": "Reading relevant chapters on ADHD dimensions and assessment"
        },
        {
          "content": "Read relevant chapters on individual variation and profiles",
          "status": "completed",
          "activeForm": "Reading relevant chapters on individual variation and profiles"
        },
        {
          "content": "Synthesize findings into structured profile dimensions",
          "status": "in_progress",
          "activeForm": "Synthesizing findings into structured profile dimensions"
        }
      ]
    }
  }
]

---

### User
> 12/1/2025, 1:49:32 PM

[
  {
    "tool_use_id": "toolu_01T2JntC5ZVPQC81L7x3nXK1",
    "type": "tool_result",
    "content": "Todos have been modified successfully. Ensure that you continue to use the todo list to track your progress. Please proceed with the current tasks if applicable"
  }
]

---

### Assistant
> 12/1/2025, 1:50:43 PM

[
  {
    "type": "text",
    "text": "Perfect! I've now read substantial material from Devon Price's \"Unmasking Autism\" covering autism dimensions, masking, and individual variation. While I wasn't able to directly access Barkley's chapters due to technical issues with the chapter IDs, I have comprehensive information from Price's work that addresses your questions about neurodivergent profiles.\n\nLet me now synthesize the findings into a structured summary of profile dimensions:\n\n---\n\n# **User Profile Dimensions for Intelligent Exploration System**\n## Research Summary from \"Unmasking Autism\" by Devon Price\n\n### **Executive Summary**\n\nBased on Devon Price's \"Unmasking Autism,\" a useful ADHD/autism user profile should capture **processing style, sensory patterns, social/communication approaches, executive functioning variations, masking strategies, and support needs**. The key insight: **profiles must be multidimensional and contextual** — not binary \"high/low functioning\" labels, but nuanced descriptions of strengths, challenges, and individual coping strategies.\n\n---\n\n## **1. Core Processing Dimensions**\n\n### **A. Information Processing Style** (from Chapter 1)\n\n**Bottom-Up vs. Top-Down Processing:**\n- **Autistic**: Process details first, build to big picture methodically\n- **Neurotypical**: Quick pattern recognition, \"gut feelings,\" mental shortcuts\n- **Profile Question**: \"Do you tend to focus on details before seeing the whole, or grasp the big picture intuitively?\"\n\n**Key Characteristics:**\n- **Deliberative processing**: Analyze pros/cons extensively, struggle with \"where to draw the line\"\n- **Reduced habituation**: Experience situations as \"new\" even when familiar\n- **High attention to detail**: Notice small features others filter out\n- **Less susceptible to cognitive biases**: More methodical decision-making\n\n**Individual Variation Factors:**\n- Some autistics can be hyperverbal and outgoing (extroverted)\n- Others are withdrawn and inhibited\n- Processing speed varies with stress, familiarity, energy levels\n- **Context matters**: Alone vs. social settings dramatically affect functioning\n\n---\n\n### **B. Sensory Processing Patterns** (Chapters 1-3)\n\n**Two Main Patterns (often both present):**\n\n1. **Sensory Avoiding**:\n   - Overwhelmed by noise, bright lights, textures\n   - Needs quiet, darkness, minimal stimulation\n   - Uses headphones, sunglasses, controlled environments\n\n2. **Sensory Seeking**:\n   - Craves loud music, spicy food, bright colors, motion\n   - Thrives on stimulation to \"overpower white noise\"\n   - Example: Roller coasters provide predictable, intense input\n\n**Profile Dimensions:**\n- **By sense modality**: Auditory, visual, tactile, proprioceptive, gustatory\n- **Tolerance thresholds**: What level of stimulation causes overwhelm?\n- **Regulation strategies**: What helps you cope? (headphones, fidgets, weighted blankets)\n- **Time-of-day/energy dependence**: \"I can handle crowds when rested, not after work\"\n\n**Critical Insight**: Same person can be both sensory-seeking AND sensory-avoiding in different domains or states.\n\n---\n\n## **2. Social & Communication Dimensions**\n\n### **A. Communication Style** (Chapters 1-2)\n\n**Spectrum includes:**\n- **Nonverbal** → Limited verbal → **Hyperverbal**\n- **Monotone** → Animated\n- **Direct/blunt** → Camouflaged politeness\n- **Echolalia** (phrase repetition) as self-regulation\n\n**Profile Questions:**\n- \"Do you use memorized scripts or prefer spontaneous conversation?\"\n- \"Do you struggle with implied meanings and sarcasm?\"\n- \"Do you find small talk exhausting vs. deep interest discussions energizing?\"\n\n---\n\n### **B. Social Interaction Patterns**\n\n**Common Variations:**\n- **Withdrawn/inhibited**: Avoids eye contact, quiet, needs explicit instructions\n- **Outgoing/extroverted**: Energetic, talkative, but may interrupt or miss social cues\n- **Social chameleon**: Adapts mannerisms/interests to groups (masking)\n\n**Key Challenges:**\n- Reading emotions on faces (deliberate analysis vs. intuitive)\n- Understanding unspoken social rules\n- Managing conversation pacing, turn-taking\n- **Rejection sensitivity**: Intense fear/pain from negative social feedback\n\n---\n\n## **3. Executive Functioning Variations**\n\n### **Core Challenges** (Referenced throughout)\n\n**Planning & Sequencing:**\n- Difficulty breaking complex tasks into logical steps\n- **Inertia starting tasks** (executive dysfunction)\n- Time management struggles (\"time blindness\" for some)\n\n**Transitions & Flexibility:**\n- High energy cost switching activities\n- Need for routines and predictability\n- Overwhelm with frequent context shifts (e.g., middle school schedule)\n\n**Working Memory & Attention:**\n- **Hyperfocus**: Can concentrate intensely on interesting tasks for hours\n- **Distractibility**: Small stimuli pull attention away\n- Trouble distinguishing \"important\" from \"nuisance\" information\n\n**Profile Approach:**\n- **Not \"good at\" vs \"bad at\"**, but **\"under what conditions does this work?\"**\n- Example: \"I can focus deeply on writing alone at night, but meetings drain me completely\"\n\n---\n\n## **4. Masking & Compensation Strategies** (Chapter 3)\n\n### **Why This Matters for AI Adaptation**\n\nMasking is **effortful social performance** that depletes energy. An AI that recognizes masking patterns can:\n- Reduce pressure to \"seem normal\"\n- Validate that exhaustion is real\n- Suggest sustainable vs. unsustainable coping\n\n### **Two Types of Masking**\n\n**A. Camouflaging** (hiding traits):\n- Forcing eye contact despite discomfort\n- Suppressing stimming (hand-flapping, rocking)\n- Hiding special interests\n- Pretending to understand when confused\n\n**B. Compensation** (workarounds):\n- Researching conversation topics beforehand\n- Using noise-canceling earbuds\n- Creating rigid schedules to manage chaos\n- Studying social rules like a foreign language\n\n### **Common Overcorrections** (Table from Chapter 3)\n\nIndividuals often **overcompensate** for feared traits:\n- Feared as \"childish\" → Mask as hyperindependent\n- Feared as \"cold\" → Mask as people-pleasing\n- Feared as \"weak\" → Mask as aggressive/tough\n- Feared as \"annoying\" → Mask as silent/agreeable\n\n**Profile Dimension**: \"What qualities were you taught to hide, and how do you compensate?\"\n\n---\n\n## **5. Individual Variation Factors**\n\n### **A. Intersectionality** (Chapter 2)\n\n**Gender, race, and class shape masking:**\n- **Women/AFAB**: Taught to be agreeable, hide aggression, mimic social play\n- **Men/AMAB**: Given more latitude for \"odd\" behavior, but expected to be tough\n- **Black/Brown individuals**: Must code-switch linguistically AND neurologically\n- **Trans/nonbinary**: Often see autism and gender identity as intertwined (\"autigender\")\n\n**Profile Question**: \"What social expectations do you face that make masking harder?\"\n\n---\n\n### **B. Co-occurring Conditions**\n\n**High Overlap With:**\n- **ADHD** (50%+ co-occurrence): Impulsivity, rejection sensitivity, inertia\n- **Anxiety/Depression**: Often consequences of masking\n- **PTSD**: From chronic bullying, abuse, or ABA therapy\n- **Eating disorders, substance use**: Maladaptive coping mechanisms\n- **Physical conditions**: EDS, GI issues, epilepsy\n\n**Critical Point**: Traits can be impossible to untangle (is hypervigilance autism or PTSD?). Profile should acknowledge **complexity, not force clean categories**.\n\n---\n\n## **6. Support Needs & \"Functioning\" Labels**\n\n### **Why \"High/Low Functioning\" is Harmful**\n\nFrom Chapter 2:\n- **\"High functioning\"**: Implies you don't need help (but you're exhausted privately)\n- **\"Low functioning\"**: Equates value with productivity\n- **Reality**: Someone can excel academically but need help dressing; or be nonverbal but brilliant\n\n### **Better Approach: Contextual Support Needs**\n\n**Dimensions:**\n- **Daily living**: Meal prep, hygiene, cleaning, executive tasks\n- **Social navigation**: When/how much support needed?\n- **Sensory regulation**: What accommodations help?\n- **Communication**: Verbal, AAC, typing, varied by context?\n- **Predictability needs**: How much routine required?\n\n**Profile Question Format**:\n- \"I can [X] independently when [conditions], but need help when [conditions]\"\n- Example: \"I can socialize at parties when I know the people and have an exit plan, but shut down at networking events\"\n\n---\n\n## **7. Assessment Approaches Recommended**\n\n### **Self-Determination vs. Formal Diagnosis** (Chapter 1)\n\n**Price advocates for self-identification because:**\n- Formal assessments are expensive ($1,200-$5,000)\n- Assessors often miss women, POC, trans people\n- Diagnosis can be used **against** you (custody, conservatorship)\n- **Gatekeeping harms those who need support most**\n\n**Profile Building Should**:\n- **Empower self-reporting**: \"Does this resonate with you?\"\n- **Avoid pathologizing language**: Frame traits as differences, not deficits\n- **Focus on practical needs**: \"What helps you think/work/rest best?\"\n\n---\n\n## **8. Practical Profile Dimensions Summary**\n\n### **Recommended Profile Structure**\n\n**Section 1: Processing Style**\n- Detail-focused or pattern-focused?\n- Deliberative or intuitive decision-making?\n- Slow to habituate to new situations?\n\n**Section 2: Sensory Preferences**\n- By modality (sound, light, touch, taste, smell, motion)\n- Seeking or avoiding patterns\n- Regulation tools that help\n\n**Section 3: Social & Communication**\n- Verbal fluency and style\n- Preference for scripts vs. spontaneity\n- Energy cost of socializing\n- Special interests and depth of focus\n\n**Section 4: Executive Functioning**\n- Task initiation and completion patterns\n- Transition difficulty\n- Time perception\n- Hyperfocus vs. distractibility triggers\n\n**Section 5: Masking & Energy**\n- What traits do you hide, and how?\n- What contexts drain you most?\n- What helps you recover?\n\n**Section 6: Support Needs**\n- Contextual: What situations require help?\n- What accommodations work best?\n- Predictability and routine needs\n\n**Section 7: Intersectional Context**\n- Cultural, gender, racial factors\n- Co-occurring conditions\n- Environmental constraints\n\n---\n\n## **Key Takeaways for IES Design**\n\n### **1. Profiles Should Be Dynamic, Not Static**\n\n- Energy levels fluctuate (burnout, overstimulation)\n- Context matters enormously\n- Allow users to update in real-time: \"Today I'm at 30% capacity\"\n\n### **2. Avoid Binary \"Functioning\" Labels**\n\n- Use **contextual descriptions**: \"I can focus deeply when alone, struggle in meetings\"\n- Celebrate **compensatory strategies** as strengths, not weaknesses\n\n### **3. Validate Masking Costs**\n\n- AI should recognize when user is pushing too hard\n- Suggest breaks, accommodations\n- Never pressure to \"seem normal\"\n\n### **4. Emphasize Self-Determination**\n\n- User defines their own experience\n- No requirement for formal diagnosis\n- Profile is a tool for self-understanding, not clinical assessment\n\n### **5. Intersectional Awareness**\n\n- Recognize that gender, race, class shape neurodivergent experience\n- Don't assume one \"autism\" or \"ADHD\" presentation\n\n---\n\n## **Sources**\n\nAll findings synthesized from:\n- **Price, Devon. (2022). *Unmasking Autism: Discovering the New Faces of Neurodiversity*. Harmony Books.**\n  - Chapter 1: \"What Is Autism, Really?\"\n  - Chapter 2: \"Who Are the Masked Autistics?\"\n  - Chapter 3: \"The Anatomy of the Mask\"\n\n---\n\nThis research-based framework provides a foundation for building user profiles that **adapt to neurodivergent thinking styles** without pathologizing or oversimplifying individual differences."
  }
]

