"""use GPT to answer questions about the input text"""

#create website to stream speech and voice to multiple agents that act in an office 

import ast  # for converting embeddings saved as strings back to arrays
from openai import OpenAI # for calling the OpenAI API
import pandas as pd  # for storing text and embeddings data
import tiktoken  # for counting tokens
import os # for getting API token from env variable OPENAI_API_KEY
from scipy import spatial  # for calculating vector similarities for search
import re

# models
EMBEDDING_MODEL = "text-embedding-ada-002"
GPT_MODEL = "gpt-4"
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

artist_song_pairs = f"""
Separate and Reconstruct:
Asymmetric Encoder-Decoder for Speech Separation

Abstract
Since the recent success of a time-domain speech separation, further improvements
have been made by expanding the length and channel of a feature sequence to
increase the amount of computation. When temporally expanded to a long sequence,
the feature is segmented into chunks as a dual-path model in most studies of
speech separation. In particular, it is common for the process of separating features
corresponding to each speaker to be located in the final stage of the network.
However, it is more advantageous and intuitive to proactively expand the feature
sequence to include the number of speakers as an extra dimension. In this paper, we
present an asymmetric strategy in which the encoder and decoder are partitioned
to perform distinct processing in separation tasks. The encoder analyzes features,
and the output of the encoder is split into the number of speakers to be separated.
The separated sequences are then reconstructed by the weight-shared decoder, as
Siamese network, in addition to cross-speaker processing. By using the Siamese
network in the decoder, without using speaker information, the network directly
learns to discriminate the features using a separation objective. With a common
split layer, intermediate encoder features for skip connections are also split for
the reconstruction decoder based on the U-Net structure. In addition, instead of
segmenting the feature sequence into chunks and processing as dual-path, we
design global and local Transformer blocks to directly process long sequences.
The experimental results demonstrated that this separation-and-reconstruction
framework is effective and that the combination of proposed global and local
Transformer can sufficiently replace the role of inter- and intra-chunk processing in
dual-path structure. Finally, the presented model including both of these achieved
state-of-the-art performance with much less computation than before in various
benchmark datasets.
1 Introduction
As a solution to the well-known cocktail party problem [12, 3], single channel speech separation [26]
has been improved since the introduction of time-domain audio separation network (TasNet) [43, 44],
which applies separation masks in the latent space instead of the short-time Fourier transform
(STFT) domain. Meanwhile, some recent works [55, 37] have shown that direct estimation of an
output representation is more effective than mask estimation, as shown in Figure 1(a). In particular,
experimental results have shown that TasNet employing a convolution-based audio encoder/decoder
performs better when the kernel length of the audio encoder is shortened [44, 42]. Therefore, the
problem of TasNet has come down to how to model a long sequence effectively. In fact, minimizing
the suppression of the sequence could be beneficial because the separation process requires generating
more output than the input received.
"""

query = f"""Use the below information scraped from the internet to answer the subsequent question.

Article:
\"\"\"
{artist_song_pairs}
\"\"\"

Question: read this paper. explain why its better suited at seperating vocals than demucs?"""


response = client.chat.completions.create(
    messages=[
        {'role': 'system', 'content': 'You answer questions about the scraped data'},
        {'role': 'user', 'content': query},
    ],
    model=GPT_MODEL,
    temperature=0,
)

print(response.choices[0].message.content)
artist_song_pairs = re.sub(r'^\d+\.\s*', '', artist_song_pairs, flags=re.MULTILINE)

artist_song_pairs = artist_song_pairs.strip().split("\n")
# Filter out entries that are not empty or whitespace
artist_song_pairs = [pair.strip() for pair in artist_song_pairs if pair.strip()]

#MTK00X where X {1-20}
#need to also do MTK003/ArtistName_SongName_Full 

base_url = "https://multitracks.cambridge-mt.com/"
# Creating the full URLs
links = [f"{base_url}{pair}_Full.zip" for pair in artist_song_pairs]

print(links)