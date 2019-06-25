#!/bin/bash

source ./standard-common-config.sh

## Users
# Example
#RUN_CHECK_CLIENT user-create --firstname Charlie --lastname Root --email root@localhost.tld --institution BellLabs --identity_id="356E5D96-B058-41F2-AD06-B59FC5BE9931" charlie

RUN_CHECK_CLIENT user-create --firstname Lincoln --lastname Bryant \
                             --email lincolnb@uchicago.edu \
                             --displayname "Lincoln Bryant" \
                             --identity_id c887eb90-d274-11e5-bf28-779c8998e810 \
                             --institution UChicago \
                             --sshpubstring "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCo3a7EUYD8qEwMBYlOzNFXXA55Lpcbgl5qlmiuwXdrOV/APr2uoIw3vYix4yYPTQPr8trfscX/NaDpVAhivlmd31ylGBjIaK/Qo0L2aTv38m9++dfflf9AdUtKdMIfddBNyOh5FlTzropoElvdVulJyGIJv6+rQeDMyaKt5HGOJ8yg+xtqcTDbfzHWVK2POP3PlcQsMg+5MkAJQDV2gvO3NxRF+ureedEtSmvEuJNUIGatM3l09FfbU9nOM9T+8xrz9tTJLMhB7QWXcd8V5IFMo+fCoSJG4qKPUrkqIHXvpNRmQ8CvEeVxwgHl/3R+Jtg8OYs7P5mmoKw4r+OBAYhL lincolnb@nam-shub" \
                             lincolnb 
RUN_CHECK_CLIENT user-create --firstname Jeremy --lastname Van \
                             --email jeremyvan@uchicago.edu \
                             --displayname "Jeremy Van" \
                             --identity_id 05e05adf-e9d4-487f-8771-b6b8a25e84d3 \
                             --institution UChicago \
                             --sshpubstring "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDRWJUVvYC5oUTIMwgr4ESyNQC9kMg77tnbDYNW/nZ5u3CS7fDyR2xKxiGZzops78lFjrY0ia5o0+j2SsZqiz2i+UHKSFp8FRS/gLdlNF+WYsBIlj4mJeVRjPt9iVZPGcjERr2894moIEc65Eb712taOleYYoetGgCzDWOTdmtjtJe2YK080q8dGgNiWr7zP1WyFDlnJXKoAObrXGzxPLBJ+Iujhzo954fpiYz8t80aBm8y0bKUCLJ2L2P2lanKOgw+oGBsQn6ox0A9CBTTlr8PbeIJvHSEMHH94vW2IlP1UDUY8sFBFcFVvnvKoZCavveddmgOcZhs1a4lVr2A8IHn JeremyVan@Jeremys-MacBook-Pro-2.local" \
                             jvan
RUN_CHECK_CLIENT user-create --firstname Robert --lastname Gardner  \
                             --email rwg@uchicago.edu \
                             --displayname "Robert Gardner" \
                             --identity_id c456b77c-d274-11e5-b82c-23a245a48997 \
                             --institution UChicago \
                             --sshpubstring "ssh-dss AAAAB3NzaC1kc3MAAACBALnbSbYpV+07kGqzkTAKUDTU62xGIFRl75wqoaY5/QPiowpU1wH5lvQUTukBu/kEsDwGtVTOEreRjYQlA678qFjrdDD5TVIh6bMSmfnrlCtS0sRreRcf2Wx3rvR9r28Sfs0yiPt1en026VQA3iO6KlYYJdgI3MPJvIKfVvGs2pntAAAAFQC9s/vtzW+iShFYj94KC9Y3/XE/jQAAAIBbDa78HK/GqC20zha9Peu9x3BWjDMLyI0EWODCWty1DB4VVjmpoZ2WwTtQfn5xpOfC0cUjPtom1wVa1/taTTPIJCQ4fJQSBJbT5zoRPmqGG5DWbUdypLjdMTjr09B3LkErenRTo1fftGraGf67mx4NcE/gCn5j8elXWHrp5pkeyAAAAIEAs5RX/ghp1vXir/unE4xQ12SYKYxBQneyAR4aTyYsKXOFdWkipEmIR9IK6KNBaReztby/qAJKqlUTS/LuAyj2G1uyOUU0zMWCigClGYYjQFHxQN/9hLGM7qVbHWA1KpIft5Ineu1mVtzoHTpDeKsg8uAiVTVnOxEKgLQ2HyGdArs= rwg@tier2-osg.uchicago.edu" \
                             rwg
RUN_CHECK_CLIENT user-create --firstname Kenyi --lastname Hurtado \
                             --email khurtado@nd.edu \
                             --displayname "Kenyi Hurtado" \
                             --identity_id a877729e-d274-11e5-a5d2-2f448d5a1c26 \
                             --institution "University of Notre Dame" \
                             --sshpubstring "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCTvU3wWWskoxN/qqqKfbrIGEiIgbHluAC7MbHvXBvYOcwDTu2PLV9IjG6zgKo1w0KNknikMTlvyp9O2NRdgwG2rrPEFMRu+zFbtGAW17eTzTtzhQuUtwin6Dlnhlj5d1h/exz+PUZglywPpl3n7tn52TANGtdNDLJ8eN6z04wIhBn8XiefRzNDSMAF97ElzhHPvrUwrqHeIqbMV7eDzlpNVF79wc0yQXBMfElKNJTqqh38oaGKIYzIK4EWtZjeTenfuRWOfIQ3j8qA/TO1KluTjpMLZ9Pze7V+6q+5RbuE3nHU/YHALAYj6C/wF3UtSGHSVzvWUYKRDmy0d77Y+fS1 kenai@MBPro" \
                             khurtado
RUN_CHECK_CLIENT user-create --firstname Suchandra --lastname Thapa \
                             --email sthapa@ci.uchicago.edu \
                             --displayname "Suchandra Thapa" \
                             --identity_id c444a294-d274-11e5-b7f1-e3782ed16687 \
                             --institution "Computation Institute" \
                             --sshpubstring "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAy6JKdUqSb01TpKdERhrO0lGA7nV2U49lFAnxeqirxImWznTibofsZG9C/1ydrRaj2Hi6V/N9brldnRH6+s0Ya2+efOyvnH50r0zoVccImFzNLmX8QB87UDJj0lwl3tFjCZMTq20Yb0dhfBd6dv237J5mmwbM6wcU6db4mMiQnpp5krUC+XbZWsHSsFxkkckaKFqme34jzFvoY6B24NH3stz8GvL6gjZ7eAOUbBO4OaobURmgWuyOfaJ7SsQUhWRZpxb4K3dCAq/vQJolfpI1ea2JTrCF06z8xI/yykpSPgxZh74y2Tknp2aGVzJdajI9JbTvim2GhlREmq5GJ7aLuw== sthapa@nsit-dhcp-250-234.uchicago.edu" \
                             sthapa
RUN_CHECK_CLIENT user-create --firstname Benjamin --lastname Tovar \
                             --email btovar@nd.edu \
                             --displayname "Benjamin Tovar" \
                             --identity_id c4686d14-d274-11e5-b866-0febeb7fd79e \
                             --institution "University of Notre Dame" \
                             --sshpubstring "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAtQ+UMDTGWe36Egol+6c6yy/WWoJRSryu25dNss2BtbygpVu4o+UVOHsYB+oQizSd364KSoeC4QiQOXgf7sBywdOuTaV81deKP1ipfdo0K23eOAA0xhJL2e3XabH31ENgtBiQxw5QO8nxnZyhUKO+mFH64E1T0ChNEnaB1YLsVQ6aOpmFf+3psMEhICuCKXGz6iAc97n0xqQqjMFoMlmpPlHskOJfd2GVbvJObID5pkXo88cmzZHTLn8Kf3H1q2ywEOyMSm00uLOkEKPtduRazGxXKPqsXjSS7ZwqQpx4mG5olGNPMp9Gqm2T1BfRCZZYBRdX1Zc6Bl2Ad5flyB3I+Q== btovar@cclws16" \
                             btovar
