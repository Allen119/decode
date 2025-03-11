<template>
    <header class="header">
           <!-- Welcome Message and Course Name Section -->
        <div class="welcome-message-section">
          <h2>{{ welcomeMessage }}</h2>
          <div class="course-name-section">
            <h3>{{ courseName }}</h3>
          </div>
        </div>
        </header>
      <div class="container">
      
        <!-- Content Section -->
        <div class="content">
          <!-- Left Panel -->
          <div class="left-panel">
            <label>Course Id</label>
            <input type="text" v-model="courseId" class="input-box" />
    
            <label>Post question</label>
            <div class= "postquestion">
              <input type="text" v-model="title" placeholder="Title" class="input-box dark" />
              <textarea v-model="description" placeholder="Description" class="input-box dark"></textarea>
            </div>
            
            <button class="post-btn" @click="postQuestion">Post</button>
    
            <!-- Questions Section -->
            <div class="questions">
              <label>Questions</label>
              <ol>
                <li v-for="(question, index) in questions" :key="index">
                  <strong>{{ question.title }}</strong>
                  <p>{{ question.description }}</p>
                </li>
              </ol>
            </div>
          </div>
    
          <!-- Right Panel -->
           <div class="right-panel1">
            <div class="right-panel">
              <label>Description</label>
              <div class="description-box">{{ courseDescription }}</div>
            </div>
            <!-- Members Button -->
              <div class="members-button-container">
                <button class="members-btn">Members</button>
              </div>
          </div>
        </div>
      </div>
    </template>
    
    <script setup>
    import { ref, onMounted } from 'vue';
    import { useRoute } from 'vue-router';
    
    const route = useRoute();
    
    // Reactive data
    const welcomeMessage = ref('Loading...');
    const courseName = ref('');
    const courseDescription = ref('');
    const courseId = ref('');
    const title = ref('');
    const description = ref('');
    const questions = ref([]);
    
    // Fetch the logged-in user's full name
    const fetchUserFullName = async () => {
      try {
        const response = await fetch('/api/method/codecampus.api.get_user_fullname', {
          method: 'GET',
          credentials: 'include',
        });
    
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
    
        const data = await response.json();
    
        if (data.message?.fullname) {
          welcomeMessage.value = `Hi ${data.message.fullname}, Welcome back!`;
        } else {
          welcomeMessage.value = 'Hi User, Welcome back!';
        }
      } catch (error) {
        console.error('Error fetching user full name:', error);
        welcomeMessage.value = 'Hi User, Welcome back!';
      }
    };
    
    // Fetch course details from query parameters
    const fetchCourseDetails = () => {
      if (route.query.courseName && route.query.courseDescription) {
        courseName.value = route.query.courseName;
        courseDescription.value = route.query.courseDescription;
      } else {
        console.log('No course details found in query parameters.');
      }
    };
    
    // Post a new question
    const postQuestion = () => {
      if (title.value && description.value) {
        questions.value.push({ title: title.value, description: description.value });
        title.value = '';
        description.value = '';
      }
    };
    
    // Fetch data when the component is mounted
    onMounted(() => {
      fetchUserFullName();
      fetchCourseDetails();
    });
    </script>
    
    <style scoped>
    .container {
      padding: 20px;
      background: hsl(0, 100%, 100%);
      min-height: 100vh;
      
    }
    
    .header {
      background: #ccc;
      padding: 1px;
      font-size: 20px;
    }
    
    
    
    /* Welcome Message and Course Name Section */
    .welcome-message-section {
      display: flex;
      align-items: center;
      justify-content: space-between; /* Align items to the left and right */
      text-align: left;
      margin: 8px 0;
    }
    
    .welcome-message-section h2 {
      font-size: 1.5rem;
      color: #252544;
      margin: 0; /* Remove default margin */
      font-weight:500;
      margin-left:10px;
    }
    
    .course-name-section h3 {
      font-size: 1.5rem;
      color: #252544;
      margin: 0; /* Remove default margin */
      font-weight:500;
      margin-right: 10px;
    }
    
    .content {
      display: flex;
      flex-direction: column;
      margin-top: 10px;
    }
    
    .left-panel {
      padding: 10px;
      background: #d3d3d3;
      margin-bottom: 10px;
      border-radius: 5px;
      position: relative; /* Ensure relative positioning for child elements */
    }
    .postquestion {
      margin: 5px 0;
       background: rgb(255, 253, 253);
      padding: 4px;
      box-sizing: border-box;
      border-radius: 5px;
    }
    .right-panel {
      height: 420px;
      padding: 10px;
      background: #d3d3d3;
      margin-bottom: 10px;
      border-radius: 35px;
      position: relative; /* Ensure relative positioning for child elements */
    }
    .right-panel1 {
      min-width: 25%;
      height: 520px;
      padding: 10px;
      background: hsl(0, 100%, 100%);
      margin-bottom: 10px;
      
      position: relative; /* Ensure relative positioning for child elements */
    }
    
    .input-box {
      width: 100%;
      margin: 5px 0;
      padding: 4px;
      box-sizing: border-box;
      border-radius: 5px;
    }
    
    .input-box.dark {
      background: #252544;
      color: white;
      border: none;
    }
    
    .post-btn,
    .members-btn {
      background: #252544;
      color: white;
      padding: 10px;
      border: none;
      cursor: pointer;
      width: 100%;
      margin-top: 10px;
      border-radius:5px;
    }
    
    .description-box {
      height: 350px;
      background: white;
      margin-top: 10px;
      border-radius: 35px;
    }
    
    .questions {
      margin-top: 20px;
    }
    
    .questions ol {
      list-style-type: decimal; /* Ordered list with numbers */
      padding-left: 20px; /* Add padding to align numbers properly */
    }
    
    .questions li {
      margin: 10px 0;
      padding: 10px;
      background: white;
      border-radius: 5px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .questions li strong {
      font-size: 1.1rem;
      color: #252544;
    }
    
    .questions li p {
      margin: 5px 0 0;
      color: #666;
    }
    
    /* Members Button Container */
    .members-button-container {
      position: absolute; /* Position the button absolutely within the right panel */
      bottom: 10px; /* Place at the bottom */
      right: 10px; /* Place at the right */
    }
    
    /* Responsive Design */
    @media (min-width: 768px) {
      .content {
        flex-direction: row;
      }
    
      .left-panel {
        flex: 2;
        margin-right: 10px;
        margin-bottom: 0;
      }
    
      .right-panel {
        flex: 1;
        margin-bottom: 0;
      }
    
      .post-btn,
      .members-btn {
        width: auto;
      }
    }
    </style>