TEAM_NUM = 4

ans = r'''Title: cars pc data: Unrestricted model
DATA: 
	FILE IS '\Users\sharpaste\Documents\program\
	testing\Python\yolo\Mplus\MET_Maydeu-Olivares_web\test.dat';

VARIABLE: 
'''

ans += '\tNAMES ARE '
for i in range(1, TEAM_NUM-1):
    ans += f"pc{i}_{i+1}-pc{i}_{TEAM_NUM} "
    if (i % 3 == 2):
        ans += '\n\t'
ans += f"pc{TEAM_NUM-1}_{TEAM_NUM};\n"

ans += r'''
! the names reflect the comparisons performed

'''

ans += '\tCATEGORICAL = '
for i in range(1, TEAM_NUM-1):
    ans += f"pc{i}_{i+1}-pc{i}_{TEAM_NUM} "
    if (i % 3 == 2):
        ans += '\n\t'
ans += f"pc{TEAM_NUM-1}_{TEAM_NUM};\n"

ans += r'''
! the data is treated as categorical

ANALYSIS:
	TYPE = MEANSTRUCTURE;
! both thresholds and tetrachoric correlations will be modeled
		
	ESTIMATOR=WLSM;
! DWLS estimation with mean corrected S-B statistic
! for mean and variance corrected S-B use WLSMV instead
	
	PARAMETERIZATION = THETA;
! the program uses a model-based diagonal matrix D to enforce
! the variance standardization

MODEL:
'''

ans += '\t'

for i in range(1, TEAM_NUM-1):
    ans += f"f{i} BY pc{i}_{i+1}-pc{i}_{TEAM_NUM}@1;\n\t"
ans += f"f{TEAM_NUM-1} BY pc{TEAM_NUM-1}_{TEAM_NUM}@1;\n\t"

print(ans)
for i in range(2, TEAM_NUM+1):
    ans += f"f{i} BY "

    for j in range(1, i):
        if (j % 3 == 0):
            ans += '\n\t\t'
        ans += f"pc{j}_{i}@-1 "
    ans += ';\n\t'
ans += '\n'
ans += '''
! this is matrix A, fixed factor loadings

! the factors are 
!		f1 = Citroen AX
!		f2 = Fiat Punto
!		f3 = Nissan Micra
!		f4 = Opel Corsa
!		f5 = Peugeot 106
!		f6 = Seat Ibiza
!		f7 = Volkswagen Polo

'''

ans += '\t'
ans += f'[pc1_2$1-pc{TEAM_NUM-1}_{TEAM_NUM}$1@0];\n'
ans += '''
! intercepts fixed at zero

'''
ans += '\t'
ans += f'[f1-f{TEAM_NUM-1}* f{TEAM_NUM}@0];\n'

ans += '''
! the means of first n-1 factors are free, the last mean is fixed at 0

'''
ans += '\t'
ans += f'pc1_2-pc{TEAM_NUM-1}_{TEAM_NUM}*.1;\n'

ans += '''
! pair specific error specific variances are free (starting value =.1)
! if these variances are to be set all equal use instead
! 	pc12-pc67(1);

! UNRESTRICTED MODEL SPECIFICATION
'''
ans += '\t'
ans += 'f1@1;\n\t'
ans += f'f{TEAM_NUM}@1;'
ans += '''
! factor variances for the first and last factors are fixed at 1
! all other factor variances are free parameters
'''
ans += '\t'

ans += f'f2 with f1*;\n\t'
for i in range(3, TEAM_NUM):
    ans += f'f{i} with f1-f{i-1}*;\n\t'
ans += '''
! factor covariances free except those involving the last object
'''
ans += f'\tf{TEAM_NUM} with f1-f{TEAM_NUM-1}@0;\n'
ans += '''
! which are fixed at 0

! CASE 3 MODEL SPECIFICATION
!	f1-f6*;
!	f7@1;
! factor variances are free except for the last one, fixed at 1
!	f2 with f1@0;
!	f3 with f1-f2@0;
!	f4 with f1-f3@0;
!	f5 with f1-f4@0;
!	f6 with f1-f5@0;
!	f7 with f1-f6@0;
! factor covariances fixed at 0

! CASE 5 MODEL SPECIFICATION
!	f1-f7@1;
! factor variances are fixed at 1
!	f2 with f1@0;
!	f3 with f1-f2@0;
!	f4 with f1-f3@0;
!	f5 with f1-f4@0;
!	f6 with f1-f5@0;
!	f7 with f1-f6@0;
! factor covariances fixed at 0

OUTPUT: TECH1; TECH5;
! use TECH1 to verify that the A matrix is properly specified
! use TECH5 to obtain the function minimum (needed for S-B nested tests)
'''

with open(r'Mplus\MET_Maydeu-Olivares_web\results.txt', 'w') as f:
    f.write(ans)
