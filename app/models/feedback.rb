class Feedback
  include ActiveModel::Model
  extend ActiveModel::Naming
  extend Enumerize

  attr_accessor :name, :email, :body

  enumerize :reason, in: [:join_moderators_team, :question_about_engine,
    :note_about_news_or_source, :general_proposal, :other]
end
