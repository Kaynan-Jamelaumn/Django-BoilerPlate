document.addEventListener('DOMContentLoaded', function () {
    const deleteButtons = document.querySelectorAll('.delete-btn');
    const modal = document.getElementById('confirmationModal');
    const confirmDeactivate = document.getElementById('confirmDeactivate');
    const cancelDeactivate = document.getElementById('cancelDeactivate');
    const csrfToken = '{{ csrf_token }}';
    let userIdToDeactivate = null;
    let targetRow = null;

    deleteButtons.forEach(button => {
        button.addEventListener('click', function () {
            userIdToDeactivate = this.getAttribute('data-user-id');
            targetRow = this.parentElement; // Store the parent <li> element
            modal.style.display = 'block';
        });
    });

    confirmDeactivate.addEventListener('click', function () {
        if (userIdToDeactivate) {
            fetch(`/deactivate_user/${userIdToDeactivate}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({}),
            })
                .then(response => {
                    if (response.ok) {
                        // Remove the row dynamically
                        if (targetRow) {
                            targetRow.remove();
                        }

                        // Show a success popup
                        const successPopup = document.createElement('div');
                        successPopup.textContent = 'User deactivated successfully!';
                        successPopup.style.position = 'fixed';
                        successPopup.style.top = '10px';
                        successPopup.style.right = '10px';
                        successPopup.style.padding = '10px 20px';
                        successPopup.style.backgroundColor = '#4caf50'; // Green background
                        successPopup.style.color = '#fff'; // White text
                        successPopup.style.borderRadius = '5px';
                        successPopup.style.boxShadow = '0px 4px 6px rgba(0,0,0,0.1)';
                        successPopup.style.zIndex = '1000';
                        document.body.appendChild(successPopup);

                        // Remove the popup after 5 seconds
                        setTimeout(() => {
                            successPopup.remove();
                        }, 5000);
                    } else {
                        console.error('Failed to deactivate the user.');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }
        modal.style.display = 'none';
    });

    cancelDeactivate.addEventListener('click', function () {
        modal.style.display = 'none';
    });
});
