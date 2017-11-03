class PostsClusterizer::RelatedPostsFinder::Document < ::TfIdfSimilarity::Document
  def initialize(post)
    super([post.title, post.description].join(" "))
  end

  private

  def tokenize(text)
    @tokens || ::UnicodeUtils.each_word(text).map do |word|
      ::ArStemmer.stem(word)
    end
  end
end
