require "matrix"

class KeywordsService
  TF_IDF_WEGHT = 4
  POST_COUNT = 1000
  HOURS_CONST = 3
  LINE_CONST = 0.8

  attr_reader :description

  def initialize(description:)
    @description = description
  end

  def keywords
    @_keywords ||= tf_idf.select { |_key, value| value > TF_IDF_WEGHT }.keys
  end

  def dependent_post
    post_list = []

    Post.where(created_at: HOURS_CONST.weeks.ago..Time.current).each do |post|
      post_list << post if count_percent(keywords, post) > LINE_CONST
    end
    post_list
  end

  private

  def count_percent(keywords, post)
    list_length = post.keywords.length > keywords.length ? keywords.length : post.keywords.length
    list_length.to_f / (post.keywords & keywords).length
  end

  def tf_idf
    list_posts = Post.last(POST_COUNT).map { |post| TfIdfSimilarity::Document.new(post.description) }
    current_model = TfIdfSimilarity::Document.new(description.gsub(/\W+/, " "))
    list_posts << current_model

    model = TfIdfSimilarity::TfIdfModel.new(list_posts)

    term_hash = {}
    current_model.terms.each do |term|
      term_hash[term] = model.tfidf(current_model, term) unless stop_words.include?(term.downcase)
    end

    term_hash
  end

  def stop_words
    @_stop_words ||= StopWord.all.map(&:name)
  end
end
