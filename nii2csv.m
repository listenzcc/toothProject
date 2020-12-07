% File: nii2csv.m
% Aim: Read *.nii and save the matrix into *.csv file

clear

for file = dir('parsed_raw_data')'
    fname = file.name;

    if endsWith(fname, '.nii')
        v = spm_vol(fname)
        dim = v.dim;
        m = spm_read_vols(v);
        mat = int16(m);
        save(fullfile('parsed_raw_data', sprintf('%s.mat', fname)), 'mat', 'dim', '-v7')
        %         csvwrite(sprintf('%s.csv', fname), m)
        %         break
    end

end
