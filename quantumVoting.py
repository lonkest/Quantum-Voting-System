# Import necessary modules from Qiskit and other libraries
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import Aer
from qiskit.quantum_info import Statevector
import numpy as np

# Function to create a voter qubit based on the given coefficients
def create_voter(candidates_coeff):
    """
    Normalize the coefficients for the candidate states to create a valid quantum state.
    
    Parameters:
    - candidates_coeff (list): A list of coefficients representing voter preferences for each candidate.

    Returns:
    - normalized_coeffs (list): A normalized list of coefficients ensuring the sum of their squares equals 1.
    """
    # Calculate the norm (length) of the coefficient vector
    norm = np.linalg.norm(candidates_coeff)
    
    # Prevent division by zero in case of a zero vector
    if norm == 0:  
        raise ValueError("Cannot normalize a zero vector.")
    
    # Normalize coefficients by dividing each by the norm
    normalized_coeffs = [coeff / norm for coeff in candidates_coeff]
    return normalized_coeffs

def adjust_values(preference, candidates):
    """
    Adjust the coefficients for candidates based on the given voter preference ranking.
    
    Parameters:
    - preference (str): A string representing the voter preference (e.g., "a>b>c>d").
    - candidates (list): A list of candidate names.

    Returns:
    - names (dict): A dictionary mapping each candidate to their calculated coefficient.
    """
    # Initialize coefficients for each candidate to 0
    names = {candidate: 0 for candidate in candidates}
    """
    
    """
    # Split the preference string to get the ranking, removing spaces
    ranking = preference.replace(' ', '').split('>')
    """
    a>b=c>d
    [a, b=c, d]
    """
    # Calculate the number of ranks based on the ranking length
    num_ranks = len(ranking)
    
    # Assign coefficients inversely proportional to the rank (higher preference -> higher value)
    for i, candidate in enumerate(ranking):
        if '=' in candidate:  # Handle tied candidates
            tied_candidates = candidate.split('=')
            for k in tied_candidates:
                if k in names:
                    names[k] = np.sqrt(num_ranks - i)  # Same coefficient for tied candidates
        else:
            if candidate in names:
                names[candidate] = np.sqrt(num_ranks - i)  # Higher value for higher preference
            
    return names

# List to store voter data
voters_data = []

# List of candidates (must be a power of 2)
candidates = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']  

preference = 'yes'
# Loop to collect voter preferences until the user decides to stop
while preference != 'no':
    preference = input("Would you like to add a new voter? yes/no ")
    if preference == 'yes':
        preference = input("Enter Voter Profile: ")
        # Adjust candidate values based on the user's input
        names = adjust_values(preference, candidates)
        # Append the adjusted values for the current voter
        voters_data.append(names)

num_candidates = len(candidates)

# Calculate the number of qubits needed per voter using log2
num_qubits_per_voter = int(np.log2(num_candidates))

# Initialize quantum and classical registers for the required qubits
num_voters = len(voters_data)  # Total number of voters
qr = QuantumRegister(num_voters * num_qubits_per_voter, name="voters")  # Quantum register for voters
cr = ClassicalRegister(num_voters * num_qubits_per_voter, name="classical")  # Classical register for measurements

# Create a quantum circuit with the defined registers
qc = QuantumCircuit(qr, cr)

# Initialize each voter's qubit state based on their coefficients
for i, voter in enumerate(voters_data):
    # Extract coefficients for each candidate
    voter_coeffs = [voter[candidate] for candidate in candidates]
    # Normalize coefficients to create the voter state
    voter_state = create_voter(voter_coeffs)
    
    # Each voter corresponds to log2(num_candidates) qubits
    qc.initialize(voter_state, qr[i * num_qubits_per_voter:(i + 1) * num_qubits_per_voter])

# Add entanglement between all voters (example: apply CNOT gates)
for i in range(num_voters - 1):
    # Example: entangle consecutive voters
    qc.cx(qr[i * num_qubits_per_voter], qr[i * num_qubits_per_voter + 1])

# Measure the qubits and store results in the classical register
qc.measure(qr, cr)

# Print the quantum circuit to the console
print(qc)

# Visualize the quantum circuit using a matplotlib plot
qc.draw(output='mpl')

# Run the quantum circuit on a statevector simulator backend
backend = Aer.get_backend('statevector_simulator')
result = backend.run(qc).result()
