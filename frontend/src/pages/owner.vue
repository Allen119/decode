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
      <p class="absolute text-[150%] right-[8%] top-1/2 transform -translate-y-1/2 text-lg text-black">
        CourseName: {{ groupDetails.groupname }}
      </p>


    </header>

    <div class="absolute bg-[#D9D9D9] w-[52%] h-[87%] top-[10%] right-[47%] ">
      <div class="absolute w-[70%] p-4 bg-[#D9D9D9] rounded-lg left-[1.5%]">
        <h3 class="text-lg mb-2 text-black font-light">Course id</h3>
        <div class="w-full p-3 bg-white rounded-md border border-gray-300 shadow-sm text-black font-light">
          {{ courseId }}
        </div>
      </div>
      <h3 class="absolute text-lg text-black font-light left-[3.5%] top-[15%]">Course Description</h3>
      <div class="absolute rounded-lg w-[66.6%] h-[27%] p-4 bg-white left-[3.2%] top-[18.5%] text-black font-light
            break-words overflow-y-auto">
        {{ groupDetails.description }}
      </div>


      <div class="absolute w-[70%] h-[50%] p-4 bg-[#D9D9D9] rounded-lg left-[1.5%] bottom-[4%]">
        <h3 class="text-lg mb-2 text-black font-light">Post question</h3>
        <!-- Make this container relative so child absolute div positions inside it -->
        <div class="relative w-full h-full">
          <div class="absolute w-[100%] h-[100%] bg-white rounded-md border border-gray-300 shadow-sm">
            <div class="absolute w-[90%] left-[5%] top-[6%] bg-[#282947] rounded-lg shadow-md">
              <input type="text" placeholder="Title" v-model="title"
                class="w-full h-full bg-transparent text-white placeholder-gray-400 border border-gray-600 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div class="absolute w-[90%] left-[5%] h-[60%] top-[23%] bg-[#282947] rounded-lg shadow-md p-4">
              <textarea placeholder="Description" v-model="description"
                class="w-full h-full bg-transparent text-white placeholder-gray-400 border border-gray-600 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 align-top resize-none break-words overflow-y-auto"></textarea>
            </div>

            <div class="absolute bottom-4 right-[5%] top-[87%]">
              <button @click="postQuestion"
                class="bg-[rgba(40,41,71,1)] text-white px-4 py-2 rounded hover:bg-[#797a9c] transition">
                Post
              </button>
            </div>
          </div>
        </div>
      </div>
      <!-- <p class="absolute text-lg text-black font-light left-[3%] top-[30%]">Questions</p> -->
      <!-- <div class="absolute bg-white w-[80%] h-[65%] top-[32%] left-[3.2%] rounded-[74px]">
        <h3 class="absolute text-lg text-black font-light left-[3%] top-[5%]">Questions</h3>
      </div> -->
    </div>
    <div class="absolute bg-[#D9D9D9] w-[40%] h-[75%] top-[16%] right-[3.5%] rounded-[74px]">
      <div class="absolute bg-white w-[92%] h-[90%] top-[5%] right-[4%] rounded-[74px] overflow-hidden">
        <h3 class="absolute text-lg text-black font-light left-[3%] top-[5%]">Questions</h3>
        <!-- List of questions - making this container scrollable while keeping the header fixed -->
        <div class="absolute left-[3%] top-[12%] w-[93%] h-[80%] overflow-y-auto pr-4">
          <ul class="text-lg text-black font-light">
            <li v-for="(question, index) in questions" :key="question.name"
              @click="fetchQuestionDetails(question.title, question.courseid)"
              class="mb-2 cursor-pointer hover:text-blue-500 transition">
              {{ index + 1 }}. {{ question.title }}
            </li>
          </ul>
        </div>




      </div>
    </div>
    <!-- Button to fetch and display members -->
    <div class="absolute bg-white w-[6%] h-[5%] bottom-[2%] right-[4%] rounded-[74px]">
      <button @click="toggleMembers"
        class="absolute bg-[rgba(40,41,71,1)] text-white px-4 py-2 rounded hover:bg-[#797a9c] transition">
        Members
      </button>
    </div>

    <!-- Members container (shows only when showMembers is true) -->
    <div v-if="showMembers"
      class="absolute bg-white p-4 rounded shadow-lg right-[4%] bottom-[8%] w-[10%] max-h-[30%] overflow-hidden">
      <div class="flex justify-between items-center mb-2">
        <h3 class="font-bold text-black">Members</h3>
        <button @click="showMembers = false" class="text-gray-500 hover:text-gray-700">
          <span class="text-xl">&times;</span>
        </button>
      </div>

      <ul v-if="members.length > 0" class="overflow-y-auto" style="max-height: calc(100% - 2rem);">
        <li v-for="(member, index) in members" :key="index"
          class="py-1 border-b text-black font-light border-gray-100 last:border-b-0">
          {{ member }}
        </li>
      </ul>
      <p v-else class="text-gray-500">No members found</p>
    </div>

    <!-- Question Details Container -->
    <div v-if="selectedQuestion" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-30 z-[999]">
      <div class="relative w-[60%] max-h-[90vh] p-6 border bg-white text-black shadow-lg rounded-lg overflow-y-auto">
        <!-- Close Button (Cross Symbol) -->
        <button @click="selectedQuestion = null"
          class="absolute top-2 right-2 bg-gray-200 text-black rounded-full w-8 h-8 flex items-center justify-center hover:bg-gray-300 transition">
          ✕
        </button>

        <!-- Title Section -->
        <h3 class="text-xl font-light mb-2">Title</h3>
        <div class="border rounded-md p-3 bg-gray-100 text-black">
          {{ selectedQuestion.title }}
        </div>

        <!-- Description Section -->
        <h3 class="text-xl font-light mt-4 mb-2">Description</h3>
        <div
          class="border rounded-md p-3 bg-gray-100 text-black font-light overflow-y-auto break-words whitespace-normal max-h-[40vh]">
          <div v-html="selectedQuestion.description"></div>
        </div>

        <!-- Submitted Users Section -->
        <h3 class="text-xl font-light mt-4 mb-2">Submitted Users</h3>
        <div class="border rounded-md p-3 bg-gray-100 text-black font-light overflow-y-auto max-h-[20vh]">
          <ul class="list-disc ml-6">
            <li v-for="answer in submittedUsers" :key="answer.filename"
              class="text-gray-600 flex justify-between items-center">
              <!-- Clicking the name triggers navigation -->
              <span @click="navigateToFile(answer.filename)" class="cursor-pointer hover:text-blue-500">
                {{ answer.fullname }}
              </span>

              <!-- Checkbox remains functional without triggering navigation -->
              <input type="checkbox"
                class="h-4 w-4 text-[rgba(40,41,71,1)] outline-none focus:ring-0 focus:ring-offset-0"
                :checked="answer.corrected === 1" @change="toggleCorrection(answer)">
            </li>
          </ul>
        </div>

        <!-- Unsubmitted Users Section -->
        <h3 class="text-xl font-light mt-4 mb-2">Unsubmitted Users</h3>
        <div class="border rounded-md p-3 bg-gray-100 text-black font-light overflow-y-auto max-h-[20vh]">
          <ul class="ml-6">
            <li v-for="user in unsubmittedUsers" :key="user.filename" class="text-gray-600">
              <span @click="navigateToFile(user.filename)" class="cursor-pointer hover:text-blue-500">
                {{ user.fullname }}
              </span>
            </li>
          </ul>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { useRoute } from 'vue-router';
import { ref, onMounted } from "vue";
import { useRouter } from 'vue-router';

const router = useRouter();

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

const title = ref("");  // Reactive variable for title
const description = ref("");  // Reactive variable for description

const postQuestion = async () => {
  try {
    const response = await fetch("http://decode.local:8080/api/method/decode.api.post_question", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        title: title.value,
        description: description.value,
        courseId: courseId.value,
      }),
    });

    const data = await response.json();
    console.log("Server Response:", data);

    if (data.message.message === "Question posted successfully!") {
      alert("Question posted!");
      title.value = ""; // Reset fields
      description.value = "";
      fetchQuestions(); // Refresh question list
    } else if (data.message.message.includes("already exists")) {
      alert("A question with this title already exists. Please use a different title.");
    } else {
      alert("Failed to post question. You may need to log in.");
    }
  } catch (error) {
    console.error("Error posting question:", error);
    alert("Network error. Try again.");
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

const members = ref([]);
const showMembers = ref(false);

const getMembers = async () => {
  try {
    const response = await fetch(`http://decode.local:8080/api/method/decode.api.get_members?course_id=${courseId.value}`);
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }
    const data = await response.json();
    console.log("Members data:", data);

    // Based on your console output, the members array is nested as data.message.message[0]
    if (data && data.message && data.message.message && Array.isArray(data.message.message)) {
      members.value = data.message.message;
    } else {
      console.error("Unexpected response format", data);
    }
  } catch (error) {
    console.error("Error fetching members:", error);
  }
};

const toggleMembers = () => {
  if (!showMembers.value) {
    getMembers(); // Fetch members when opening the container
  }
  showMembers.value = !showMembers.value;
};

const selectedQuestion = ref(null); // Stores selected question details
const submittedUsers = ref([]); // Stores list of submitted users
const unsubmittedUsers = ref([]); // Stores list of unsubmitted users

const fetchQuestionDetails = async (questionTitle) => {
  if (!questionTitle || !courseId.value) return;

  try {
    const response = await fetch(
      `http://decode.local:8080/api/method/decode.api.getTitleDetails?questionTitle=${encodeURIComponent(questionTitle)}&courseId=${courseId.value}`
    );
    const data = await response.json();
    console.log("Question Details:", data);

    if (data.message?.status === "success") {
      // ✅ Assigning question details properly
      selectedQuestion.value = {
        title: data.message.question.title,
        description: data.message.question.description
      };

      // ✅ Assigning submitted and unsubmitted users correctly
      submittedUsers.value = data.message.submitted_answers || [];
      unsubmittedUsers.value = data.message.unsubmitted_answers || [];

      console.log("Selected Question:", selectedQuestion.value);
      console.log("Submitted Users:", submittedUsers.value);
      console.log("Unsubmitted Users:", unsubmittedUsers.value);
    } else {
      console.error("Error:", data.message);
    }
  } catch (error) {
    console.error("Error fetching question details:", error);
  }
};



const toggleCorrection = async (answer) => {
  // Toggle the corrected value
  answer.corrected = answer.corrected === 1 ? 0 : 1;

  try {
    const response = await fetch("http://decode.local:8080/api/method/decode.api.updateCorrection", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        answer_id: answer.filename, // Assuming filename is the unique identifier
        corrected: answer.corrected, // New value after toggling
      }),
    });

    const data = await response.json();

    // Access the nested status in the message object
    if (data.message && data.message.status === "success") {
      console.log("Correction updated successfully!");
    } else {
      console.error("Error updating correction:", data.message?.message || "Unknown error");
    }
  } catch (error) {
    console.error("Network error:", error);
  }
};

const navigateToFile = (filename) => {
  if (filename) {
    router.push({ name: 'filecode1', params: { uuid: filename } });
  }
};

onMounted(() => {
  fetchQuestions();
  fetchGroupDetails();
  getMembers();
});

</script>