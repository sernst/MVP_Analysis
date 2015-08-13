import pandas

df = pandas.DataFrame(
    data=[
        (1, 2, 3),
        (3, 4, 5),
        (2, 3, 4),
        (4, 5, 6) ],
    columns=['A', 'B', 'C'])

df.loc[:, 'D'] = 12

print(df.D, type(df.D))

sub = df[df.A < 3]
sub.loc[:, 'D'] = 4
print(sub)

df = sub.combine_first(df)
print(sub)
print(df)
