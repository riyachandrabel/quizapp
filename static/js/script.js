
// document.querySelectorAll('.quiz-form').forEach(form => {
//     form.addEventListener('submit', async event => {
//         event.preventDefault();
//         const formData = new FormData(form);

//         try {
//             const response = await fetch(form.action, {
//                 method: 'POST',
//                 body: formData,
//             });

//             const result = await response.json();
//             if (result.success) {
//                 document.querySelector(`#score-${result.quiz_id}`).textContent = `${result.score}`;
//                 showToast('Quiz submitted successfully!', 'success');
//             } else {
//                 showToast(result.message, 'error');
//             }
//         } catch (error) {
//             showToast('An error occurred. Please try again.', 'error');
//         }
//     });
// });

// function showToast(message, type) {
//     const toast = document.createElement('div');
//     toast.className = `toast ${type}`;
//     toast.textContent = message;
//     document.body.appendChild(toast);
//     setTimeout(() => toast.remove(), 3000);
// }