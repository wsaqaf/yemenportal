require "matrix"

class KeywordsService
  attr_reader :description, :config

  def initialize(description:)
    @description = description
    @config = Rails.application.config_for(:tf_idf_settings)
  end

  def keywords
    @_keywords ||= tf_idf.select { |_key, value| value > config["min_weight"] }.keys
  end

  def dependent_post
    post_list = []

    Post.where(created_at: config["hours_period"].hours.ago..Time.current).each do |post|
      post_list << post if count_percent(keywords, post) > config["min_percent"]
    end
    post_list
  end

  private

  def count_percent(keywords, post)
    list_length = post.keywords.length > keywords.length ? keywords.length : post.keywords.length
    equal_length = (post.keywords & keywords).length
    equal_length.zero? ? 0 : (equal_length.to_f / list_length)
  end

  def tf_idf
    list_posts = Post.last(config["post_count"]).map { |post| TfIdfSimilarity::Document.new(post.description) }
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
