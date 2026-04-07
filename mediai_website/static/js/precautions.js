/* precautions.js — Full precaution database for all 41 diseases */
const PRECAUTIONS = {
  "AIDS": {
    desc: "A chronic immune system disease caused by the human immunodeficiency virus (HIV) that impairs the body's ability to fight infections.",
    symptoms: ["fatigue","weight_loss","fever","night sweats","swollen lymph nodes","recurrent infections"],
    do: ["Take antiretroviral therapy (ART) exactly as prescribed","Attend regular check-ups and CD4/viral load tests","Eat a nutritious balanced diet to support immunity","Practice safe sex using condoms","Get vaccinated against flu, pneumonia, hepatitis B","Inform sexual partners of your status","Join a support group for mental well-being"],
    avoid: ["Sharing needles or syringes","Unprotected sex","Skipping ART doses","Alcohol and recreational drugs that weaken immunity","Raw or undercooked meat and unpasteurized products","Contact with people who have active infections"],
    emergency: ["High fever (above 38.5°C) with stiff neck","Sudden vision changes or blindness","Difficulty breathing or severe cough","Confusion or loss of consciousness","Severe weight loss in a short period"]
  },
  "Acne": {
    desc: "A skin condition that occurs when hair follicles become clogged with oil and dead skin cells, causing pimples, blackheads, and whiteheads.",
    symptoms: ["pus_filled_pimples","blackheads","skin_rash","nodal_skin_eruptions","scurring"],
    do: ["Wash face twice daily with a gentle, non-comedogenic cleanser","Use oil-free, non-comedogenic moisturisers and sunscreen","Apply topical treatments containing benzoyl peroxide or salicylic acid","Change pillowcases frequently","Stay hydrated and eat a balanced diet","Consult a dermatologist for persistent or severe acne"],
    avoid: ["Touching or picking your face","Greasy or heavy makeup","Tight clothing over affected areas","Dairy and high-glycaemic foods (may worsen acne in some people)","Harsh scrubbing of the skin","Stress (can worsen breakouts)"],
    emergency: ["Sudden spread of severe cysts across the face","Signs of skin infection (increasing redness, warmth, swelling)","Scarring despite treatment","Severe emotional distress related to acne appearance"]
  },
  "Alcoholic hepatitis": {
    desc: "Inflammation of the liver caused by excessive alcohol consumption, which can lead to serious liver damage.",
    symptoms: ["jaundice","abdominal_pain","nausea","vomiting","fatigue","loss_of_appetite"],
    do: ["Stop drinking alcohol completely — this is the most important step","Eat a nutritious, low-sodium diet","Stay well hydrated with water and juices","Take prescribed medications and vitamin supplements","Attend all medical follow-up appointments","Seek alcohol addiction counselling or rehabilitation"],
    avoid: ["Alcohol in any form","Over-the-counter pain medications like ibuprofen or aspirin","High-fat, processed foods","Herbal supplements not approved by your doctor","Skipping meals"],
    emergency: ["Vomiting blood","Black tarry stools (internal bleeding)","Extreme confusion or disorientation","Yellowing of skin worsening rapidly","Severe abdominal swelling"]
  },
  "Allergy": {
    desc: "An immune system reaction to a foreign substance that is typically not harmful to most people, such as pollen, pet dander, or certain foods.",
    symptoms: ["continuous_sneezing","watering_from_eyes","redness_of_eyes","itching","skin_rash","runny_nose"],
    do: ["Identify and avoid your specific allergy triggers","Take antihistamines or prescribed allergy medication","Use air purifiers indoors","Keep windows closed during high pollen seasons","Shower after outdoor activities to remove allergens","Carry an epinephrine auto-injector if prescribed"],
    avoid: ["Known allergens (foods, pollen, pet dander, dust mites)","Aspirin or NSAIDs if you have aspirin-sensitive asthma","Alcohol (can worsen allergic reactions)","Stress (weakens immune response)"],
    emergency: ["Difficulty breathing or wheezing","Throat swelling or tightening","Rapid heartbeat","Dizziness or fainting after allergen exposure (anaphylaxis)","Sudden drop in blood pressure"]
  },
  "Arthritis": {
    desc: "Inflammation of one or more joints, causing pain and stiffness that can worsen with age. The most common types are osteoarthritis and rheumatoid arthritis.",
    symptoms: ["joint_pain","swelling_joints","movement_stiffness","knee_pain","hip_joint_pain"],
    do: ["Exercise regularly — low-impact activities like swimming, cycling, yoga","Apply hot or cold packs to affected joints","Maintain a healthy weight to reduce joint stress","Take prescribed anti-inflammatory medications","Use assistive devices (braces, canes) when needed","Attend physiotherapy sessions"],
    avoid: ["High-impact activities that stress joints (running, jumping)","Sitting in one position for long periods","Processed foods, excess sugar, and red meat","Smoking (worsens inflammation)","Ignoring pain and skipping rest"],
    emergency: ["Sudden severe joint swelling and heat","Joint becomes completely immobile","Fever accompanying joint pain (may indicate septic arthritis)","Chest pain in rheumatoid arthritis patients"]
  },
  "Bronchial Asthma": {
    desc: "A condition where the airways narrow and swell, producing extra mucus, making breathing difficult and triggering coughing and wheezing.",
    symptoms: ["breathlessness","cough","wheezing","chest_pain","mucoid_sputum"],
    do: ["Always carry your rescue inhaler","Take controller medications as prescribed — even when feeling fine","Monitor peak flow readings daily","Identify and avoid asthma triggers","Get vaccinated against flu and pneumonia","Create an asthma action plan with your doctor"],
    avoid: ["Smoking and secondhand smoke","Known triggers: dust, mold, pet dander, pollen","Cold air without covering mouth/nose","Strenuous exercise without warm-up and preventer inhaler","NSAIDs and aspirin (can trigger attacks in some people)","Stress and strong emotions without coping strategies"],
    emergency: ["Rapid worsening of breathing despite using inhaler","Lips or fingernails turning blue","Unable to speak in full sentences","Severe wheezing or no wheezing (silent chest — very dangerous)","Peak flow below 50% of personal best"]
  },
  "Cervical spondylosis": {
    desc: "Age-related wear and tear affecting the spinal discs in the neck, causing pain, stiffness, and sometimes nerve compression.",
    symptoms: ["neck_pain","back_pain","weakness_in_limbs","dizziness","loss_of_balance"],
    do: ["Perform gentle neck stretches and physiotherapy exercises","Use a supportive pillow for sleeping","Maintain good posture while sitting and using devices","Apply heat or cold packs to the neck","Take prescribed pain relievers or anti-inflammatories","See a physiotherapist regularly"],
    avoid: ["Prolonged screen time without breaks","Sleeping on your stomach","Heavy lifting that strains the neck","Sudden jerky neck movements","High-impact activities without medical clearance"],
    emergency: ["Sudden loss of bladder or bowel control","Severe weakness or numbness in arms/legs","Sudden inability to walk","Progressive worsening of neurological symptoms"]
  },
  "Chicken pox": {
    desc: "A highly contagious viral infection causing an itchy rash with small fluid-filled blisters, primarily affecting children but preventable by vaccine.",
    symptoms: ["skin_rash","itching","fatigue","high_fever","blister","red_spots_over_body"],
    do: ["Stay home and isolate until all blisters have crusted over","Take antiviral medication if prescribed within 24 hours of rash","Apply calamine lotion to relieve itching","Keep fingernails short and clean to prevent scratching","Drink plenty of fluids","Take paracetamol for fever (NOT aspirin in children)"],
    avoid: ["Scratching blisters (causes scarring and infection)","Aspirin in children (risk of Reye's syndrome)","Contact with pregnant women, newborns, and immunocompromised individuals","Public places until blisters have all crusted","Ibuprofen (may increase risk of skin infection)"],
    emergency: ["Breathing difficulty or chest pain","Rash spreading to eyes","Skin becomes red, warm, and swollen (bacterial infection)","Severe headache, stiff neck, or confusion (encephalitis)","Fever lasting more than 4 days or above 39°C"]
  },
  "Chronic cholestasis": {
    desc: "A condition where bile flow from the liver is reduced or blocked, leading to accumulation of bile in the liver and bloodstream.",
    symptoms: ["itching","yellowish_skin","yellowing_of_eyes","dark_urine","loss_of_appetite","fatigue"],
    do: ["Take prescribed medications (ursodeoxycholic acid)","Follow a low-fat diet","Stay hydrated","Take fat-soluble vitamin supplements (A, D, E, K)","Attend regular liver function tests","Avoid alcohol completely"],
    avoid: ["Alcohol and recreational drugs","High-fat meals","Medications that affect the liver without doctor approval","Herbal supplements without medical clearance","Ignoring worsening jaundice"],
    emergency: ["Sudden intense abdominal pain (biliary colic)","High fever with chills (cholangitis)","Rapid worsening of jaundice","Confusion or altered consciousness","Vomiting blood"]
  },
  "Common Cold": {
    desc: "A viral infection of the upper respiratory tract, mainly caused by rhinoviruses, with symptoms including runny nose, sore throat, and cough.",
    symptoms: ["continuous_sneezing","runny_nose","cough","mild_fever","throat_irritation","congestion"],
    do: ["Rest as much as possible","Drink plenty of warm fluids (water, herbal tea, broth)","Gargle with warm saltwater for sore throat","Use saline nasal drops or steam inhalation","Take paracetamol for fever and body aches","Wash hands frequently to prevent spreading"],
    avoid: ["Close contact with others to avoid spreading the virus","Smoking and alcohol","Cold drinks and ice cream","Going outdoors in cold weather without covering up","Antibiotics (ineffective against viral infections)"],
    emergency: ["Breathing difficulty or wheezing","Fever above 39.5°C persisting for more than 3 days","Severe headache with stiff neck","Chest pain","Symptoms lasting more than 10 days without improvement"]
  },
  "Dengue": {
    desc: "A mosquito-borne viral disease common in tropical regions, characterised by high fever, severe headache, and joint and muscle pain.",
    symptoms: ["high_fever","headache","pain_behind_the_eyes","joint_pain","skin_rash","nausea","vomiting"],
    do: ["Rest completely","Drink plenty of fluids — water, ORS, coconut water, fruit juices","Take paracetamol only for fever and pain","Monitor platelet count regularly as advised","Stay under a mosquito net","See a doctor immediately if symptoms worsen","Keep the patient's environment mosquito-free"],
    avoid: ["Aspirin or ibuprofen (increase risk of bleeding)","Physical exertion","Mosquito exposure — use repellent and nets","Self-medicating without medical guidance","Dehydration — very dangerous in dengue"],
    emergency: ["Severe abdominal pain","Bleeding from nose, gums, or in urine/stools","Vomiting blood","Rapid breathing","Cold clammy skin (dengue shock syndrome)","Platelet count dropping below 20,000"]
  },
  "Diabetes": {
    desc: "A chronic condition that affects how the body processes blood sugar (glucose), requiring careful management of diet, exercise, and medication.",
    symptoms: ["fatigue","weight_loss","excessive_hunger","polyuria","irregular_sugar_level","blurred_and_distorted_vision"],
    do: ["Monitor blood sugar levels regularly","Take insulin or oral medications as prescribed","Follow a diabetic-friendly diet (low glycaemic index foods)","Exercise at least 30 minutes daily","Keep feet clean and inspect daily for wounds","Attend regular HbA1c tests and eye/kidney check-ups","Carry fast-acting glucose (glucose tablets or juice) at all times"],
    avoid: ["Sugary drinks, sweets, white bread, white rice","Skipping meals","Missing medication doses","Smoking","Barefoot walking (risk of foot wounds)","Excessive alcohol"],
    emergency: ["Blood sugar above 300 mg/dL or below 70 mg/dL","Extreme confusion or unconsciousness (hypoglycaemia)","Fruity breath with nausea (diabetic ketoacidosis)","Severe vomiting or inability to keep food down","Chest pain or difficulty breathing"]
  },
  "Dimorphic hemorrhoids (piles)": {
    desc: "Swollen veins in the rectum and anus that cause discomfort, bleeding, and itching, made worse by straining during bowel movements.",
    symptoms: ["pain_in_anal_region","bloody_stool","irritation_in_anus","pain_during_bowel_movements","constipation"],
    do: ["Eat a high-fibre diet (fruits, vegetables, whole grains)","Drink 8–10 glasses of water daily","Soak in a warm sitz bath for 10–15 minutes several times daily","Apply over-the-counter haemorrhoidal creams","Avoid straining during bowel movements","Exercise regularly to prevent constipation","Use stool softeners if prescribed"],
    avoid: ["Straining during bowel movements","Sitting on the toilet for long periods","Spicy foods that irritate the digestive tract","Alcohol and caffeine (cause dehydration)","Heavy lifting","Scratching the anal area"],
    emergency: ["Heavy rectal bleeding","Bleeding that doesn't stop within 10 minutes","Severe pain that doesn't respond to home treatment","Prolapsed haemorrhoid that cannot be pushed back","Signs of infection (fever, pus, increasing pain)"]
  },
  "Drug Reaction": {
    desc: "An adverse response to a medication that can range from mild skin rashes to severe systemic reactions affecting multiple organ systems.",
    symptoms: ["skin_rash","itching","burning_micturition","anxiety","fever"],
    do: ["Stop taking the suspected medication immediately","Inform your doctor about the reaction right away","Document the medication name, dose, and timing of reaction","Take prescribed antihistamines or corticosteroids","Carry a list of medications you are allergic to","Wear a medical alert bracelet for severe allergies"],
    avoid: ["Taking the same medication or related drugs again","Self-medicating without informing your doctor","Delay in seeking medical help for severe reactions","Starting new medications without disclosing previous reactions"],
    emergency: ["Severe skin blistering (Stevens-Johnson syndrome)","Throat swelling or difficulty breathing (anaphylaxis)","Rapid pulse and drop in blood pressure","Loss of consciousness","High fever with widespread skin peeling"]
  },
  "Fungal infection": {
    desc: "An infection caused by fungal organisms that can affect the skin, nails, hair, or deeper body tissues, common in warm and moist areas.",
    symptoms: ["itching","skin_rash","nodal_skin_eruptions","dischromic_patches"],
    do: ["Keep affected areas clean and dry","Apply prescribed antifungal creams or oral medications","Wear loose, breathable cotton clothing","Change socks and underwear daily","Wash towels and bedding frequently in hot water","Complete the full course of antifungal treatment"],
    avoid: ["Sharing towels, clothing, or personal items","Walking barefoot in public showers or pools","Tight synthetic clothing","Excessive sweating without changing clothes","Stopping treatment early even if symptoms improve"],
    emergency: ["Fever with spreading red rash","Rash spreading rapidly despite treatment","Swelling and warmth suggesting bacterial superinfection","Infection spreading to nails or scalp without improvement"]
  },
  "GERD": {
    desc: "Gastroesophageal reflux disease — a chronic condition where stomach acid flows back into the oesophagus, causing heartburn and discomfort.",
    symptoms: ["acidity","chest_pain","indigestion","vomiting","stomach_pain"],
    do: ["Eat smaller, more frequent meals","Sit upright for at least 2 hours after eating","Elevate the head of your bed by 15–20 cm","Take prescribed proton pump inhibitors or antacids","Maintain a healthy weight","Wear loose-fitting clothing"],
    avoid: ["Fatty, fried, and spicy foods","Chocolate, coffee, citrus fruits, and tomatoes","Alcohol and carbonated drinks","Lying down immediately after meals","Smoking","Tight clothing around the waist","Large meals close to bedtime"],
    emergency: ["Difficulty swallowing or pain when swallowing","Vomiting blood or coffee-ground material","Unexplained weight loss","Chest pain (must rule out heart attack)","Black or tarry stools (bleeding)"]
  },
  "Gastroenteritis": {
    desc: "Inflammation of the stomach and intestines usually caused by viral or bacterial infection, leading to diarrhoea, vomiting, and abdominal cramps.",
    symptoms: ["vomiting","diarrhoea","stomach_pain","nausea","dehydration","mild_fever"],
    do: ["Drink oral rehydration solution (ORS) frequently in small sips","Rest completely","Gradually reintroduce bland foods (rice, banana, toast)","Wash hands thoroughly and frequently","Take prescribed medications","Monitor for signs of dehydration"],
    avoid: ["Dairy products until recovered","Fatty, spicy, or fried foods","Alcohol and caffeine","Antidiarrhoeal medications without doctor advice in some cases","Sharing utensils, towels, or food","Returning to work or school until symptom-free for 48 hours"],
    emergency: ["No urination for 8+ hours (severe dehydration)","Blood in vomit or stools","High fever above 39°C","Extreme confusion or drowsiness","Sunken eyes and dry mouth in children","Diarrhoea lasting more than 3 days"]
  },
  "Heart attack": {
    desc: "A medical emergency where blood supply to part of the heart is blocked, causing heart muscle damage. Requires immediate medical attention.",
    symptoms: ["chest_pain","breathlessness","sweating","vomiting","fast_heart_rate","pain_behind_the_eyes"],
    do: ["Call emergency services (112/108) IMMEDIATELY","Chew an aspirin (325mg) if available and not allergic","Rest in a comfortable position (usually sitting)","Loosen tight clothing","Perform CPR if the person is unresponsive and not breathing","Keep the person calm and still"],
    avoid: ["Driving yourself to the hospital","Physical exertion of any kind","Eating or drinking while waiting for help","Ignoring symptoms hoping they go away","Taking nitroglycerin without a prescription"],
    emergency: ["ANY chest pain lasting more than 5 minutes — CALL 112 NOW","Pain spreading to arm, jaw, or back","Cold sweat with chest pain","Sudden shortness of breath","This entire disease IS the emergency — act immediately"]
  },
  "Hepatitis A": {
    desc: "A highly contagious liver infection caused by the hepatitis A virus, spread through contaminated food and water, usually self-limiting.",
    symptoms: ["yellowish_skin","dark_urine","nausea","vomiting","fatigue","loss_of_appetite","mild_fever"],
    do: ["Rest completely — fatigue may last weeks","Drink plenty of fluids","Eat small, easily digestible meals","Avoid alcohol completely","Practice strict hand hygiene","Get vaccinated if not already vaccinated","Notify close contacts to get vaccinated"],
    avoid: ["Alcohol (extremely dangerous to the liver)","Fatty foods","Medications metabolised by the liver (consult doctor)","Donating blood","Preparing food for others during active infection","Physical exertion"],
    emergency: ["Worsening jaundice over several days","Severe abdominal pain","Confusion or disorientation (liver failure)","Not passing urine","Bleeding tendency (bruising easily)"]
  },
  "Hepatitis B": {
    desc: "A viral infection attacking the liver that can cause both acute and chronic disease, spread through blood, sexual contact, and from mother to child.",
    symptoms: ["yellowish_skin","dark_urine","fatigue","vomiting","loss_of_appetite","receiving_blood_transfusion"],
    do: ["Take prescribed antiviral medications without fail","Avoid alcohol completely","Get vaccinated family members and close contacts","Eat a healthy, well-balanced diet","Attend regular liver function and viral load tests","Use condoms to prevent sexual transmission","Practice safe injection practices"],
    avoid: ["Alcohol in any amount","Sharing needles, razors, or toothbrushes","Unprotected sexual contact","Medications harmful to the liver without doctor approval","Herbal supplements (can damage liver)"],
    emergency: ["Sudden confusion or memory loss (hepatic encephalopathy)","Yellow skin worsening rapidly","Vomiting blood","Swollen abdomen (ascites)","Blood in stools"]
  },
  "Hepatitis C": {
    desc: "A viral infection causing liver inflammation, spread mainly through blood contact, that can silently cause cirrhosis over many years.",
    symptoms: ["yellowish_skin","dark_urine","fatigue","nausea","loss_of_appetite","receiving_unsterile_injections"],
    do: ["Take the complete course of direct-acting antiviral therapy (DAA)","Attend all medical follow-up appointments","Avoid alcohol completely","Eat a liver-friendly diet","Get vaccinated for Hepatitis A and B","Inform your doctor before any dental or surgical procedures"],
    avoid: ["Sharing needles, syringes, or drug equipment","Alcohol","Paracetamol in large doses without doctor guidance","Iron supplements unless specifically prescribed","Donating blood or organs"],
    emergency: ["Progressive confusion (liver failure)","Vomiting blood (variceal bleeding)","Rapid worsening of jaundice","Severe abdominal distension","Uncontrollable bruising or bleeding"]
  },
  "Hepatitis D": {
    desc: "A liver infection that only occurs in people already infected with Hepatitis B. Superinfection leads to more severe liver disease.",
    symptoms: ["yellowish_skin","dark_urine","fatigue","abdominal_pain","loss_of_appetite"],
    do: ["Follow all Hepatitis B management guidelines","Take antiviral medication as prescribed","Get regular liver ultrasound and biopsy as recommended","Eat a nutritious, low-fat diet","Avoid all alcohol","Inform all healthcare providers of both infections"],
    avoid: ["Alcohol completely","Sharing any blood-contaminated items","Drugs metabolised by the liver without guidance","Herbal or traditional remedies not prescribed","Ignoring worsening symptoms"],
    emergency: ["Sudden mental confusion","Jaundice worsening significantly","Vomiting blood","Severe abdominal pain","Uncontrolled bleeding"]
  },
  "Hepatitis E": {
    desc: "A liver disease caused by the hepatitis E virus, transmitted through contaminated water, particularly dangerous in pregnant women.",
    symptoms: ["yellowish_skin","dark_urine","fatigue","nausea","loss_of_appetite","mild_fever"],
    do: ["Rest completely","Drink safe, purified water only","Eat nutritious, easily digestible foods","Avoid alcohol completely","Pregnant women should be hospitalised for close monitoring","Take prescribed supportive medications"],
    avoid: ["Contaminated water and street food","Alcohol","Raw or undercooked shellfish","Medications harmful to the liver","Physical exertion"],
    emergency: ["In pregnancy — ANY sign of liver failure is an EMERGENCY","Sudden confusion or loss of consciousness","Severe jaundice with bleeding","Fetal movement changes in pregnant women","Inability to eat or drink"]
  },
  "Hypertension": {
    desc: "Persistently elevated blood pressure putting extra strain on the heart and blood vessels, increasing risk of heart attack and stroke.",
    symptoms: ["headache","chest_pain","dizziness","lack_of_concentration","loss_of_balance","fast_heart_rate"],
    do: ["Take blood pressure medication exactly as prescribed — never skip","Monitor blood pressure at home daily","Follow a low-sodium (DASH) diet","Exercise 30 minutes on most days","Maintain a healthy weight","Reduce stress through meditation, yoga, deep breathing","Limit alcohol to minimal amounts","Quit smoking"],
    avoid: ["High-sodium foods (chips, processed meats, pickles)","Excessive caffeine","Alcohol and smoking","Stress without management strategies","Cold and flu medications with decongestants (raise BP)","Stopping medications without doctor advice"],
    emergency: ["Blood pressure above 180/120 mmHg (hypertensive crisis)","Severe headache with visual changes","Sudden chest pain or shortness of breath","Confusion or difficulty speaking","Severe nausea with very high BP reading"]
  },
  "Hyperthyroidism": {
    desc: "A condition where the thyroid gland produces too much thyroid hormone, speeding up the body's metabolism and causing various symptoms.",
    symptoms: ["fast_heart_rate","weight_loss","sweating","anxiety","enlarged_thyroid","excessive_hunger"],
    do: ["Take antithyroid medications (methimazole/propylthiouracil) as prescribed","Attend regular thyroid function tests","Eat a calcium and vitamin D rich diet","Rest adequately","Use sunglasses to protect eyes (in Graves' disease)","Discuss radioiodine or surgical options with your doctor"],
    avoid: ["Iodine-rich foods (seaweed, iodised salt in excess)","Caffeine and stimulant drinks","Strenuous exercise until thyroid levels are controlled","Smoking (worsens eye disease in Graves')","Stopping medications without medical advice"],
    emergency: ["Thyroid storm: very high fever, rapid irregular heartbeat, confusion — CALL 112","Chest pain or extreme shortness of breath","Sudden paralysis","Severe eye pain or vision loss","Extreme agitation and high fever together"]
  },
  "Hypoglycemia": {
    desc: "A condition where blood sugar levels drop too low, causing symptoms ranging from shakiness and confusion to loss of consciousness.",
    symptoms: ["fatigue","restlessness","sweating","irregular_sugar_level","dizziness","palpitations"],
    do: ["Follow the 15-15 rule: eat 15g fast carbs, wait 15 min, recheck blood sugar","Keep glucose tablets, juice, or regular soda accessible at all times","Eat regular meals and snacks — do not skip","Inform family/colleagues about condition and what to do","Wear a medical ID bracelet","Monitor blood sugar before driving or exercising","Carry glucagon kit if prescribed"],
    avoid: ["Skipping meals or fasting without medical guidance","Excessive alcohol on an empty stomach","Strenuous exercise without adjusting food/insulin","Delaying treatment when symptoms start","Driving when blood sugar may be low"],
    emergency: ["Blood sugar below 54 mg/dL that doesn't improve with food","Loss of consciousness","Seizures","Unable to swallow safely — use glucagon injection","Confused and combative patient — do not force feed"]
  },
  "Hypothyroidism": {
    desc: "A condition where the thyroid gland doesn't produce enough thyroid hormone, slowing down the body's metabolism and causing fatigue and weight gain.",
    symptoms: ["fatigue","weight_gain","constipation","brittle_nails","enlarged_thyroid","cold_hands_and_feets"],
    do: ["Take levothyroxine medication at the same time daily on an empty stomach","Attend regular thyroid function tests (TSH every 6–12 months)","Eat a balanced diet with adequate iodine and selenium","Exercise regularly to combat fatigue and weight gain","Get adequate sleep","Inform your doctor if pregnant (dose adjustment needed)"],
    avoid: ["Taking calcium, iron, or antacids within 4 hours of thyroid medication","Excessive soy and cruciferous vegetables","Stopping medication without medical advice","Excessive iodine supplements","Cigarette smoking"],
    emergency: ["Myxoedema coma: extreme fatigue, low body temperature, confusion","Very slow heart rate with unconsciousness","Difficulty breathing","Severe swelling of the body","Seizures"]
  },
  "Impetigo": {
    desc: "A highly contagious bacterial skin infection common in children, causing red sores that burst and form honey-coloured crusts.",
    symptoms: ["skin_rash","itching","blister","red_sore_around_nose","yellow_crust_ooze"],
    do: ["Apply prescribed antibiotic cream to affected areas","Take oral antibiotics if prescribed (for widespread infection)","Gently clean sores with soap and water before applying cream","Keep nails short to prevent scratching and spreading","Wash hands frequently","Keep affected child away from school until 48 hours after starting treatment","Change and wash bedding, towels, and clothing daily"],
    avoid: ["Touching or picking at sores","Sharing towels, clothing, or personal items","Scratching (spreads infection and worsens scarring)","Contact sports until fully healed","Close contact with newborns or immunocompromised individuals"],
    emergency: ["Rapidly spreading infection despite treatment","Sores becoming deeper (ecthyma)","Fever and swollen lymph nodes","Signs of kidney problems (swollen ankles, reduced urine — post-strep complications)"]
  },
  "Jaundice": {
    desc: "Yellowing of the skin and eyes caused by excess bilirubin in the blood, indicating underlying liver, gallbladder, or blood conditions.",
    symptoms: ["yellowish_skin","yellowing_of_eyes","dark_urine","yellow_urine","fatigue","loss_of_appetite"],
    do: ["Get investigated immediately to find the underlying cause","Rest completely","Stay hydrated with water and fresh juices","Follow a liver-friendly diet (low-fat, high-carbohydrate)","Take prescribed medications","Avoid alcohol completely","Attend follow-up tests regularly"],
    avoid: ["Alcohol (extremely harmful to liver)","Fatty or oily foods","Self-medication","Herbal remedies without medical clearance","Strenuous physical activity"],
    emergency: ["Jaundice with high fever and chills (cholangitis)","Confusion or altered mental state","Vomiting blood","Severe abdominal pain","Rapidly deepening yellow colour","No urine output"]
  },
  "Malaria": {
    desc: "A life-threatening disease caused by Plasmodium parasites transmitted through the bite of infected female Anopheles mosquitoes.",
    symptoms: ["high_fever","chills","sweating","headache","vomiting","muscle_pain","fatigue"],
    do: ["Take prescribed antimalarial medications (artemisinin-based combination therapy)","Complete the FULL course of medication","Rest and stay hydrated with clean fluids","Use ORS for dehydration","Use mosquito nets and repellent","Monitor temperature regularly","Seek medical help if no improvement in 24 hours"],
    avoid: ["Exposure to mosquitoes — use nets, repellents, and long clothing","Aspirin or NSAIDs (increase bleeding risk in severe malaria)","Self-treatment with incomplete doses","Delay in seeking treatment (can become severe rapidly)"],
    emergency: ["Unconsciousness or severe confusion (cerebral malaria)","Difficulty breathing","Convulsions","High fever above 40°C","Inability to keep fluids down","Blood in urine (blackwater fever)"]
  },
  "Migraine": {
    desc: "A neurological condition characterised by intense, throbbing headaches often on one side of the head, with nausea, vomiting, and sensitivity to light.",
    symptoms: ["headache","nausea","vomiting","visual_disturbances","pain_behind_the_eyes","dizziness"],
    do: ["Take prescribed triptans or pain relief at the FIRST sign of migraine","Rest in a dark, quiet room","Apply cold or warm compress to head and neck","Stay hydrated before, during, and after an episode","Keep a migraine diary to identify triggers","Take prescribed preventive medications daily","Practice regular sleep and meal schedules"],
    avoid: ["Known triggers: stress, bright lights, loud sounds, strong smells","Skipping meals or irregular sleep","Alcohol (especially red wine)","Caffeine withdrawal","Excessive screen time","Over-using pain medications (causes rebound headaches)"],
    emergency: ["Worst headache of your life (thunderclap)","Headache with stiff neck, fever, or rash","Sudden vision loss, numbness, or difficulty speaking","Headache after head injury","New headache pattern in a person over 50"]
  },
  "Osteoarthritis": {
    desc: "A degenerative joint disease where cartilage breaks down, causing pain, stiffness, and swelling, most commonly in knees, hips, and hands.",
    symptoms: ["joint_pain","knee_pain","hip_joint_pain","movement_stiffness","painful_walking","swelling_joints"],
    do: ["Exercise regularly — swimming, walking, and cycling are ideal","Maintain a healthy weight","Use hot/cold therapy on painful joints","Take prescribed pain relievers or NSAIDs","Use knee braces or walking aids if needed","Attend physiotherapy sessions","Consider corticosteroid injections if recommended"],
    avoid: ["High-impact activities (running, jumping, contact sports)","Prolonged standing or sitting in one position","Excess weight — increases joint load dramatically","Ignoring pain and overexerting","Stopping physiotherapy when pain improves temporarily"],
    emergency: ["Sudden severe joint pain with fever (possible joint infection)","Complete inability to move a joint","Rapidly increasing joint swelling","Severe pain after a fall or injury"]
  },
  "Paralysis (brain hemorrhage)": {
    desc: "Loss of muscle function in part of the body following bleeding into or around the brain, requiring immediate emergency treatment.",
    symptoms: ["weakness_of_one_body_side","slurred_speech","loss_of_balance","headache","altered_sensorium"],
    do: ["CALL 112 IMMEDIATELY — time is critical","Keep the person lying still and calm","Note the exact time symptoms started","Do not give food or water","If conscious, position on their side (recovery position)","Begin rehabilitation as soon as medically cleared","Attend physiotherapy, occupational therapy, and speech therapy consistently"],
    avoid: ["Any delay in calling emergency services","Giving aspirin without medical instruction","Moving the person unnecessarily","Leaving the person unattended","Skipping rehabilitation sessions"],
    emergency: ["ANY sudden one-sided weakness or facial drooping — USE FAST TEST","F: Face drooping, A: Arm weakness, S: Speech difficulty, T: Time to call 112","Sudden severe headache like a thunderclap","Loss of consciousness","Rapid deterioration — EVERY MINUTE COUNTS for brain haemorrhage"]
  },
  "Peptic ulcer disease": {
    desc: "Open sores that develop on the inner lining of the stomach and the upper part of the small intestine, caused by H. pylori or NSAIDs.",
    symptoms: ["stomach_pain","indigestion","vomiting","acidity","loss_of_appetite"],
    do: ["Take prescribed antibiotics (for H. pylori) for the FULL course","Take proton pump inhibitors or H2 blockers as directed","Eat small, frequent meals","Choose bland, non-irritating foods","Drink milk or antacids with meals for immediate relief","Test and treat H. pylori infection"],
    avoid: ["NSAIDs (ibuprofen, aspirin, naproxen) without medical supervision","Smoking and alcohol","Spicy, acidic, and fatty foods","Coffee, tea, and carbonated drinks","Stress (increases acid production)","Eating large meals or skipping meals"],
    emergency: ["Vomiting blood or coffee-ground vomit","Black, tarry stools","Sudden severe abdominal pain (perforation)","Feeling faint with abdominal pain","Rapidly worsening pain not relieved by antacids"]
  },
  "Pneumonia": {
    desc: "Infection causing inflammation of the air sacs in one or both lungs, which may fill with fluid or pus, causing cough, fever, and difficulty breathing.",
    symptoms: ["cough","high_fever","breathlessness","chest_pain","rusty_sputum","fatigue","phlegm"],
    do: ["Take the complete course of prescribed antibiotics (even when feeling better)","Rest completely","Drink plenty of fluids to loosen mucus","Take prescribed fever reducers","Use a humidifier to ease breathing","Practice deep breathing exercises","Get vaccinated against pneumococcal and flu in future","Follow up with a chest X-ray after recovery"],
    avoid: ["Smoking and secondhand smoke","Cold environments without adequate warmth","Strenuous activity during treatment","Stopping antibiotics early","Alcohol (weakens immune system)"],
    emergency: ["Severe breathing difficulty or rapid breathing","Oxygen saturation below 94% (if measured)","Blue lips or fingernails","Confusion or altered mental state","Fever not responding to medication","Chest pain worsening with breathing"]
  },
  "Psoriasis": {
    desc: "A chronic autoimmune skin disease causing rapid buildup of skin cells, forming scales and red patches that can be itchy and sometimes painful.",
    symptoms: ["skin_rash","silver_like_dusting","small_dents_in_nails","skin_peeling","inflammatory_nails","joint_pain"],
    do: ["Apply prescribed topical corticosteroids or vitamin D analogues","Moisturise skin daily — apply thick creams after bathing","Bathe in lukewarm water with oatmeal or coal tar","Take prescribed systemic medications or biologics","Get safe sun exposure (15–20 minutes) as phototherapy","Follow up regularly with a dermatologist","Manage stress through yoga and meditation"],
    avoid: ["Scratching or picking scales","Harsh soaps and hot water","Smoking and alcohol (trigger flares)","Skin injuries (Koebner phenomenon)","Infections (can trigger flares — treat promptly)","Certain medications (lithium, beta-blockers, antimalarials) without guidance"],
    emergency: ["Erythrodermic psoriasis: red, burning skin over most of the body","Pustular psoriasis: white, pus-filled blisters","High fever with widespread skin involvement","Rapid deterioration requiring hospitalisation"]
  },
  "Tuberculosis": {
    desc: "A serious bacterial infection primarily affecting the lungs, caused by Mycobacterium tuberculosis, spread through airborne droplets.",
    symptoms: ["cough","blood_in_sputum","fatigue","weight_loss","high_fever","night sweats","loss_of_appetite"],
    do: ["Take ALL prescribed TB medications (DOTS regimen) WITHOUT FAIL for 6–9 months","Cover your mouth when coughing or sneezing","Ensure good ventilation in living spaces","Eat a protein-rich, nutritious diet","Attend all follow-up sputum tests and chest X-rays","Inform close contacts for TB screening and preventive treatment","Isolate until confirmed non-infectious"],
    avoid: ["Missing even a single dose of TB medication (leads to drug resistance)","Alcohol and smoking","Close contact with others until declared non-infectious","Sharing utensils or sleeping in crowded spaces during active TB","Stopping treatment when feeling better"],
    emergency: ["Coughing up large amounts of blood","Severe breathing difficulty","Chest pain with breathing","Meningitis symptoms (stiff neck, severe headache, confusion)","Multi-drug resistant TB signs — lack of improvement after 2 months of treatment"]
  },
  "Typhoid": {
    desc: "A bacterial infection caused by Salmonella typhi, spread through contaminated food and water, causing high fever, abdominal pain, and weakness.",
    symptoms: ["high_fever","headache","fatigue","vomiting","diarrhoea","toxic_look_(typhos)","nausea"],
    do: ["Take the complete antibiotic course as prescribed","Rest completely","Drink only boiled or purified water","Eat soft, easily digestible foods (khichdi, curd, bananas)","Monitor temperature every 4–6 hours","Practice strict hand hygiene","Isolate from food preparation until fully recovered"],
    avoid: ["Raw foods, salads, and street food during recovery","Cold water and dairy products","Physical exertion","Missing antibiotic doses","Aspirin for fever (risk of bleeding)"],
    emergency: ["Intestinal perforation: sudden severe abdominal pain with rigid abdomen","Intestinal bleeding: blood in stools","High persistent fever despite antibiotics for more than 5 days","Extreme confusion or altered consciousness","Severe dehydration with no urine output"]
  },
  "Urinary tract infection": {
    desc: "An infection in any part of the urinary system — kidneys, ureters, bladder, and urethra — most commonly affecting the bladder.",
    symptoms: ["burning_micturition","continuous_feel_of_urine","bladder_discomfort","foul_smell_of_urine","spotting_urination"],
    do: ["Take the complete course of prescribed antibiotics","Drink 8–10 glasses of water daily to flush bacteria","Urinate frequently — don't hold urine","Wipe from front to back after using the toilet","Urinate before and after sexual activity","Wear loose, breathable cotton underwear","Take cranberry supplements (may help prevent recurrence)"],
    avoid: ["Delaying urination when you feel the urge","Using harsh soaps or bubble baths near the genital area","Tight synthetic underwear","Stopping antibiotics early","Alcohol and caffeine (irritate the bladder)","Douching"],
    emergency: ["Fever above 38.5°C with chills and back pain (kidney infection)","Blood in urine","Severe pain in the lower back or side","Nausea and vomiting with UTI symptoms","UTI not improving after 3 days of antibiotics"]
  },
  "Varicose veins": {
    desc: "Enlarged, twisted veins that are swollen and raised above the skin surface, commonly occurring in the legs, caused by weakened vein valves.",
    symptoms: ["prominent_veins_on_calf","swollen_legs","painful_walking","swollen_blood_vessels","fatigue"],
    do: ["Elevate your legs above heart level for 15–20 minutes several times daily","Walk and exercise regularly to improve circulation","Wear prescribed compression stockings","Maintain a healthy weight","Take breaks from prolonged standing or sitting","Sleep with legs elevated on a pillow","Consult a vascular surgeon for treatment options (sclerotherapy, laser, surgery)"],
    avoid: ["Prolonged standing or sitting without breaks","Tight clothing that constricts the waist or legs","High-heeled shoes","Hot baths and direct heat on legs","Crossing legs while sitting","Being overweight — worsens venous pressure"],
    emergency: ["Sudden severe pain and swelling in one leg (DVT — deep vein thrombosis)","Redness, warmth, and tenderness along a vein","Skin ulcer or open sore near the ankle","Varicose vein bleeding — apply firm pressure and go to emergency","Shortness of breath and chest pain (possible pulmonary embolism from DVT)"]
  },
  "Vertigo (Paroxysmal Positional Vertigo)": {
    desc: "A sudden sensation that you or your environment is spinning or moving, most commonly caused by displaced crystals in the inner ear.",
    symptoms: ["spinning_movements","unsteadiness","loss_of_balance","dizziness","nausea","vomiting"],
    do: ["Perform the Epley manoeuvre as instructed by your doctor","Move slowly and carefully when changing positions","Sit or lie down immediately when dizziness strikes","Use a walking aid to prevent falls","Sleep with the head slightly elevated","Avoid activities that may cause falls","Attend vestibular rehabilitation physiotherapy"],
    avoid: ["Sudden head movements","Looking up or down quickly","Bending over rapidly","Caffeine, alcohol, and high-sodium foods (worsen inner ear fluid balance)","Driving during episodes","Activities at heights during active episodes"],
    emergency: ["New severe headache with vertigo (possible stroke)","Double vision, difficulty swallowing, or slurred speech","Loss of consciousness","Vertigo lasting hours without position change","Progressive one-sided hearing loss with vertigo"]
  }
};

// Make globally available
window.PRECAUTIONS = PRECAUTIONS;
