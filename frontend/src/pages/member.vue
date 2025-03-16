<template>
    <div id="app" class="font-sans h-screen w-screen bg-white text-white flex flex-col"
        :style="{ fontFamily: 'Inter, sans-serif' }">
        <!-- Header -->
        <header class="bg-[rgba(217,217,217,1)] text-purple-700 p-4 flex justify-between items-center h-[7%] relative"
            :style="{ fontFamily: 'Inter, sans-serif' }">
            <!-- Logo and User ID Section -->
            <div class="flex items-center gap-4">
                <img src="@/assets/images/logo.png" alt="Logo" class="object-contain"
                    :style="{ maxHeight: '80%', width: '10%', height: 'auto' }" />
                <span class="text-[150%] text-black">Hi user welcome back</span>
            </div>

            <!-- Course Name (Centered and 30% from the left) -->
            <p
                class="absolute text-[150%] right-[10%] top-1/2 transform -translate-y-1/2 text-lg text-black font-light">
                <!-- JAva -->
            </p>


        </header>

        <div class="absolute bg-[#D9D9D9] w-[52%] h-[87%] top-[10%] right-[47%] ">
            <div class="absolute w-[70%] p-4 bg-[#D9D9D9] rounded-lg left-[1.5%] top-[1.5%]">
                <h3 class="text-lg mb-2 text-black font-light">Course owner</h3>
                <div class="w-full p-3 bg-white rounded-md border border-gray-300 shadow-sm text-black font-light">
                    {{ groupDetails.groupowner }}
                </div>
            </div>

            <div class="absolute w-[70%] p-4 bg-[#D9D9D9] rounded-lg left-[1.5%] top-[15%]">
                <h3 class="text-lg mb-2 text-black font-light">Course name</h3>
                <div class="w-full p-3 bg-white rounded-md border border-gray-300 shadow-sm text-black font-light">
                    {{ groupDetails.groupname }}
                </div>
            </div>
            <!-- <p class="absolute text-lg text-black font-light left-[3%] top-[30%]">Questions</p> -->
            <div class="absolute bg-white w-[80%] h-[65%] top-[32%] left-[3.2%] rounded-[50px]">
                <h3 class="absolute text-lg text-black font-light left-[3%] top-[5%]">Questions</h3>
                <div class="absolute left-[3%] top-[12%] w-[93%] h-[80%] overflow-y-auto pr-4" >
                    <ul class="text-lg text-black font-light">
                        <li v-for="(question, index) in questions" :key="question.name" class="mb-2">
                            {{ index + 1 }}. {{ question.title }}
                        </li>
                    </ul>
                </div>
            </div>
        </div>
        <div class="absolute bg-[#D9D9D9] w-[40%] h-[75%] top-[16%] right-[3.5%] rounded-[74px]">
            <div class="absolute bg-white w-[92%] h-[90%] top-[5%] right-[4%] rounded-[74px]">
                <h3 class="absolute text-lg text-black font-light left-[3%] top-[5%]">Description</h3>
                <div class="absolute left-[3%] top-[12%] w-[90%] h-[80%] p-0 text-black font-light
            break-words overflow-y-auto">
                    {{ groupDetails.description }}
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { useRoute } from 'vue-router';
import { ref, onMounted } from "vue";

const route = useRoute();
const courseId = ref(route.params.courseId);
const groupDetails = ref({
    groupname: '',
    groupowner: '',
    description: ''
});

const fetchGroupDetails = async () => {
    try {
        const response = await fetch(
            `http://decode.local:8080/api/method/decode.api.get_group_details?courseId=${courseId.value}`
        );
        const data = await response.json();

        // Extract just the fields we need from the response
        if (data.message && !data.message.error) {
            groupDetails.value = {
                groupname: data.message.groupname,
                groupowner: data.message.groupowner,
                description: data.message.description
            };
            console.log("Group details:", groupDetails.value);
        } else {
            console.error("API Error:", data.message?.error || "Unknown error");
        }
    } catch (error) {
        console.error("Error fetching group details:", error);
    }
};

const questions = ref([]);

const fetchQuestions = async () => {
  try {
    const response = await fetch(`http://decode.local:8080/api/method/decode.api.get_questions?courseId=${courseId.value}`, {
      method: "GET",
      credentials: "include",
    });
    const data = await response.json();
    if (data.message && data.message.questions) {
      questions.value = data.message.questions; // Store filtered questions
    } else {
      console.error("Unexpected API response format:", data);
    }
  } catch (error) {
    console.error("Error fetching questions:", error);
  }
};


onMounted(() => {
    fetchQuestions();
    fetchGroupDetails();
});

</script>