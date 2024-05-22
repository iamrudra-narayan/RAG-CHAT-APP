from .retrieval import llm_name, openai_client, get_top_retrieval, rerank, top_k_retrieval

# Ask Questions Method
def ask_questions(llm_name, prompt):
    response = openai_client.chat.completions.create(
      model=llm_name,
      messages=[
        {"role": "system", "content": "You are a helpful research assistant."},
        {"role": "user", "content": prompt},
      ])

    return response.choices[0].message.content

# Question and Answer Bot Method
def question_answer_bot(user_query, namespace, llm_name=llm_name):
    print(1234)
    _, matches = get_top_retrieval(user_query, namespace)
  
    print(123)
    retrieved_formatted_data = []
    for i in range(len(matches)):
        retrieved_formatted_data.append({
          "id":matches[i].id,
          "text":matches[i].metadata['doc'],
          "meta": matches[i].metadata
       })

    ranked_matches = rerank(user_query, retrieved_formatted_data) 
   
    context = "\n\n".join([doc.get('text') for doc in ranked_matches][0:10])

    final_prompt : str
    invalid_question_response_prompt = f"""
              If the given question that is delimited with triple quotes is not related with the given 
              context that is delimited with triple quotes or \
              you donot have or find any appropriate answer from the given context, \
              then provide a humble and gentle answer of not having the proper answer and make sure you give answer \
              without giving the explanation of the question. \ 
              Only give the pertains of the context or documents for instruct the user \ 
              of which related questions they should ask to you.

              question: ```{user_query}```
              context: ```{context}```
              """
    
    # Provide Valid Question
    base_prompt = f"""
                Your task is to perform the following actions: 
                      1 - Look for grammatical mistakes and spelling mistakes in the question that is delimited with triple quotes.
                      2 - If there are any spelling mistakes and grammatical mistakes then correct it.
                      3 - After correcting the spelling mistakes and grammatical mistakes, rephrase the question that is delimited with triple quotes in a refined way.
                      4 - Provide the final question after following the above steps in the  below format.
              If the question that is delimited with triple quotes is related with the given context that is delimited with triple quotes,        
              then use the following format to answer:
              <final question>
              Make sure to provide the final question only.

              If the question that is delimited with triple quotes is not related with context that is delimited with triple quotes,
              then make sure you will only provide the response text that is <response not available>.

              question: ```{user_query}```
              context: ```{context}```
            """
    base_prompt_response = ask_questions(llm_name, base_prompt)
    print("base_prompt_response:",base_prompt_response)

    # After provide valid question
    if base_prompt_response == "<response not available>":
        prompt = invalid_question_response_prompt
    else: 

        prompt = f"""
                You will get a question delimited with by triple quotes.
 
                Your task is to extract relevant information from \ 
                the given context that is delimited by triple quotes.
 
                your task to give answer on context extraction
                If the given question is other than related to the given context or \
                you donot have or find any appropriate answer, \
                then provide a humble and gentle answer of not having the proper answer and \
                without giving the explanation of the question. \ 
                Only give the pertains of the context or documents for instruct the user \ 
                of which related questions they should ask to you.
 
                question: ```{user_query}``` \
                context: ```{context}```
            """
        # option_prompt = f"""
        #         input response is :{base_prompt_response}.
        #               Verify if their input response falls into one of the provided choices. The choices are as follows:
        #                   Category 1 - Brief Answer                                                                                                
        #                   Category 2 - Detailed Answer                                     
        #                   Category 3 - Step by Step Detailed Answer
                          
        #               Provide only the option. For example: "Brief Answer" or "Detailed Answer" or "Step by Step Detailed Answer".  
        #         """
        # response_type =  ask_questions(llm_name, option_prompt)
        # # print(response_type)
        
        # if response_type == "Step by Step Detailed Answer":
        #     final_prompt = f"""
        #                     input answer is :{base_prompt_response}.
        #                     Your task is to rephrase the input answer in step by step details format.
        #                     For example:
        #                         Step 1: [Explanation or instruction for the first step]
        #                         Step 2: [Explanation or instruction for the second step]
        #                         Step 3: [Explanation or instruction for the third step]
        #                         Step 4: [Explanation or instruction for the fourth step]
        #                         Step 5: [Explanation or instruction for the fifth step]
        #                         Step 6: [Explanation or instruction for the sixth step]
        #                         Step 7: [Explanation or instruction for the seventh step]
        #                         Step 8: [Explanation or instruction for the eighth step]
        #                         Step 9: [Explanation or instruction for the ninth step]
        #                         Step N [Explanation or instruction for the tenth step]
        #                     There can be different N no. of steps depending on the answer.

        #                      Your task is to check the number of steps in the input answer.
        #                      'Provide your answer in a structured format, avoiding generic responses.'
        #               """
        # elif response_type == "Detailed Answer":
        #     final_prompt = f"""    
        #                     input response is :{base_prompt_response}.
        #                     Convert the input response in the {response_type} format.
        #                     Follow the below instructions to get refined answer 
        #                     If input response is  Brief Answer then provide the answer in paragraph in 150-200 words.                                                        
        #                     Make sure to provide only the answer.No need to provide the category of answer(i.e Detailed Answer or Brief Answer)
        #                      'Provide your answer in a structured format, avoiding generic responses.'
        #                 """
        # else:
        #     final_prompt = f"""    
        #                     input response is :{base_prompt_response}.
        #                     Convert the input response in the {response_type} format.
        #                     Follow the below instructions to get refined answer 
        #                     If input response is  Brief Answer then provide the answer in paragraph in 50-60 words.                                                        
        #                     Make sure to provide only the answer.No need to provide the category of answer(i.e Detailed Answer or Brief Answer)
        #                      'Provide your answer in a structured format, avoiding generic responses.'
        #                 """

   
    return ask_questions(llm_name, prompt)


# If the given question is about the steps related answers, \
#                 then your task is to rephrase the answer in step by step format.
#                 For example:
#                     Step 1: [Explanation or instruction for the first step]
#                     Step 2: [Explanation or instruction for the second step]
#                     Step 3: [Explanation or instruction for the third step]
#                     Step 4: [Explanation or instruction for the fourth step]
#                     Step N [Explanation or instruction for the tenth step]
#                 There can be different N no. of steps depending on the answer.
 
#                 If any question you get that have short or brief answers, \
#                 then provide answers very shortly or briefly with proper details.
 
#                 If any question you get that have Detailed Answer, \
#                 then follow the below instructions to get refined answer:
#                 -If input response is  Brief Answer then provide the answer in paragraph in 150-200 words.                                                        
#                 -Make sure to provide only the answer.No need to provide the category of answer(i.e Detailed Answer or Brief Answer).
 